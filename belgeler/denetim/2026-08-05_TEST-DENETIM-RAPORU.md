# DİMA — TEST DENETİM RAPORU

> **Üç bölüm.** **BÖLÜM 1** ölçülen çıktı *(teşhis yok)* · **BÖLÜM 2** kök nedenler
> *(çözüm yok)* · **BÖLÜM 3** kök çözümler *(kapı ölçütü — uygulama emri değil)*.
> Kardeş belge: [`2026-08-05_ANLAMA-KATMANI.md`](./2026-08-05_ANLAMA-KATMANI.md) —
> `route()`'un anlama yarısını denetler; Bölüm 3 onu **yeniden ölçer ve birleştirir**.
>
> 🔴 **SAYILAR DAMGALIDIR.** Her ölçüm hangi commit'te koşulduğuyla birlikte yazılıdır
> ve HEAD ilerledikçe **bayatlar**. Bir sayı tutmuyorsa bulguyu çürütmez — *"yeniden
> ölçülmeli"* der. Bulgu ancak **mekanizma ortadan kalkmışsa** çürür.
>
> **BÖLÜM 1 · TEST ÇIKTILARI ve SINIFLANDIRMA**
> Bu bölüm **yalnız ölçülen çıktıyı** taşır. **Kök neden analizi YOKTUR** — kullanıcı
> kararıyla ayrı bölüme bırakılmıştır. Buradaki her satır bir **gözlemdir**, bir teşhis
> değildir.

| | |
|---|---|
| **Damga** | `9b2410e` · dal `wren-bağımsız` · çalışma ağacı **temiz** (0 kirli dosya) |
| **Tarih** | 2026-08-05 |
| **Denetçi rolü** | salt-okunur · depoya yazma yok · geliştirme yok |
| **Makine** | 20 çekirdek · 38,88 GiB RAM · konteyner CPU sınırı yok |
| **Test imajı** | `dima-test` @ `sha256:8148dab0538aa` |
| **Envanter** | **255** test dosyası · **29** `lab/` aracı · **87** `app/*.py` modülü |
| **Kaynak kütükler** | `<scratchpad>/suit.log` (koşum A) · `hepsi.log` (48.041 satır, koşum B) · `tsc.log` · `eslint.log` |

**Koşum hijyeni** *(kılavuz §3'e uygun)*: `-d` + `--name` + `docker wait` + `docker logs` +
`docker rm -f`. `--rm` **kullanılmadı**. İki test konteyneri **hiçbir an paralel koşmadı**.
🔴 **Canlı-LLM koşumu YAPILDI** (§4B) — kullanıcının açık talimatıyla ve **kontrollü**:
senaryo başına ayrı konteyner, tur arası 5 sn, senaryo arası 15 sn. Kılavuz §3'ün
*"yerel kapıda ASLA"* kuralı **geliştirme kapısı** içindir; bu bir **denetim turudur** ve
kuralın gerekçesi olan kota sınırına (10 istek/10 sn) **uyularak** koşulmuştur.

---

## 0 · ÖZET TABLO

| Kaynak | Sonuç |
|---|---|
| **Süit — koşum A** (doğrudan `pytest`, tek süreç) | 🔴 **112 başarısız** · 3503 geçti · 25 atlandı · **19 dk 15 sn** |
| **Süit — koşum B** (`kapi.py --hepsi`, paralel) | 🔴 **23 başarısız** · 3605 geçti · 25 atlandı · 3 xfailed · **6 dk 03 sn** |
| **Korpus kapısı** | 🔴 **KIRMIZI** |
| **Gerçek-dünya korpusu** | 🟢 yeşil — ama **42 sessiz-yanlış** + **14 katalog sızıntısı** taşıyor |
| **eval.run** | 🟡 adım ✓ — **precision −%12,7** · coverage −%0,9 · det. pay −%1,8 |
| **Konuşma senaryoları** | 🟡 adım ✓ — **1 sınıf ⊘ ÖLÇÜLEMEDİ** |
| **`kapi.py --hepsi` genel** | 🔴 **✗ TAM KAPI (dört adım) KIRMIZI** |
| **TypeScript** (`tsc --noEmit`) | 🟢 **0 hata** |
| **ESLint** | 🔴 **5 hata** · 5 uyarı |
| **Ortam** | 🔴 `dima-wren-engine` **5 gündür çökme döngüsünde** |
| **Yetim modül** | 🟢 5 (4'ü belgede meşru · `main` yanlış-pozitif) — **yeni yok** |
| **Bayrak kaydı** | 🟢 42 ↔ 41 · tek fark **gerekçeli** |
| **Deneyim süiti — CANLI** (15 senaryo · 58 tur · tek tek) | 🔴 **✅40 · ❌2 · ⊘3** — ve 🔴 **58 turun yalnız 2'si LLM'e gitti**; OpenRouter devri **⊘ tetiklenmedi** |
| 🔴 **Denetim sondası — CANLI** (51 senaryo · **178 tur** · çok-turlu insani) | 🔴 **13 yanlış/katalog-dışı · 50 sessiz seçim · 10 boş · 3 çapa kaybı** — *"kesin doğru" sayılabilecek tur **SIFIR*** |

---

## 1 · 🔴 BULGU 0 — İKİ KOŞUM FARKLI SONUÇ VERDİ

Aynı depo, aynı damga (`9b2410e`), aynı imaj, aynı mount, aynı `DIMA_VQR_EMBEDDER=off`.
**Tek fark: çağırma biçimi.**

| | Koşum A | Koşum B |
|---|---|---|
| Komut | `python -m pytest -q -p no:warnings --tb=short -rf` | `python lab/kapi.py --hepsi` |
| **Başarısız** | **112** | **23** |
| Geçen | 3503 | 3605 |
| Atlanan | 25 | 25 |
| xfailed | 0 | 3 |
| **Toplanan** *(hesaplanan)* | **3640** | **3656** |
| Süre | 1155,72 sn (**19:15**) | 363,77 sn (**6:03**) |
| CPU | ~%96 (**1 çekirdek**) | %1046–1413 (**10–14 çekirdek**) |

**Küme farkı — test adlarıyla kesiştirilerek ölçüldü:**

| | Adet |
|---|---|
| Koşum A başarısız | 112 |
| Koşum B başarısız | 23 |
| **ORTAK** *(her iki koşumda da başarısız)* | **22** |
| 🔴 **Yalnız koşum A** | **90** |
| 🔴 **Yalnız koşum B** | **1** — `test_responsive.py::test_SAYFA_PAYI_seritle_BIRLIKTE_donuyor` |

**Doğrulama:** A = 90 + 22 = **112** ✓ · B = 1 + 22 = **23** ✓

**İki gözlem, ikisi de ham:**
1. **90 başarısız test koşum B'de tekrar üretilemedi**; buna karşılık **1 test yalnız
   koşum B'de** başarısız oldu (koşum A'da hiç görünmedi).
2. **16 test toplanma farkı** (3640 ↔ 3656) — hangi tarafın fazladan/eksik topladığı bu
   bölümde **ölçülmedi**.

> ⚠ Bu rapor **hangi koşumun doğru olduğunu iddia etmez.** İkisi de ölçüldü, ikisi de
> kayda geçiyor. Ayrım kök-neden bölümünün konusudur.

---

## 2 · `kapi.py --hepsi` — BEŞ ADIM

Nihai verdikt: **`✗ TAM KAPI (dört adım) KIRMIZI`**

| # | Adım | Verdikt | Aracın kendi özet satırı |
|---|---|---|---|
| 1 | korpus kapısı | 🔴 **✗** | `TOPLAM doğru-cube: %93.4 (taban %93.2) ✅` |
| 2 | gerçek-dünya korpusu | 🟢 ✓ | `kapı yeşil · {'vaka': 2297, 'kabul': 1100, 'dogru': 63, 'sessiz_yanlis': 42}` |
| 3 | tam süit | 🔴 **✗** | `23 failed, 3605 passed, 25 skipped, 3 xfailed in 363.77s` |
| 4 | eval.run | 🟢 ✓ | `baseline'a göre: precision -12.7% · coverage -0.9% · deterministik pay -1.8%` |
| 5 | konuşma senaryoları | 🟢 ✓ | `⊘ ÖLÇÜLEMEDİ: vaka ne geçti ne kaldı — ölçüm ön koşulu sağlanmadı` |

> ⚠ **Adım 1'in özet satırı `✅` işareti taşıyor ama adım `✗`.** Aracın kendi verdikti
> (`nl_corpus` çıktısının son satırı): **`KAPI KIRMIZI — dondurulmuş tabana göre gerileme
> var.`** İkisi aynı çıktıda birlikte duruyor; bu bir çelişki değil, **iki farklı ölçütün
> ayrı ayrı raporlanması**.

---

### 2.1 · KORPUS KAPISI 🔴

**Şirket bazında koşum sonucu:**

| Şirket | Tur | Erişim (OK) | Doğru-cube | Yanlış | Discovery |
|---|---|---|---|---|---|
| 🔴 **boyahane** | **satır ÜRETİLMEDİ** | — | — | — | — |
| atiksan | 1447 | 1005 (**%69**) | 931/949 = **%98** | 18 | 0 |
| gulteks | 1618 | 1112 (**%68**) | 995/1040 = **%95** | 45 | 0 |
| gitas | 2479 | 1793 (**%72**) | 1517/1696 = **%89** | **179** | 0 |

**Dondurulmuş tabana kıyas** *(taban: `FAZ 0 · adım 1-8`)*:

| Ölçüt | Ölçülen | Taban | Verdikt |
|---|---|---|---|
| 🔴 **boyahane** | — | — | **HATA — kıyaslanamadı** |
| atiksan erişim | %69 | %69 | ✅ |
| gulteks erişim | %69 | %68 | ✅ |
| gitas erişim | %72 | %72 | ✅ |
| **TOPLAM doğru-cube** | **%93,4** | %93,2 | ✅ |
| **SEMANTİK VAKA** | **236/254 = %92,9** | %92,1 | ✅ · şişme katsayısı **14,5×** |

**Ölçülen: kırmızıyı veren tek kalem `boyahane`'nin ölçüm satırının hiç üretilmemesidir.**
Diğer dört ölçütün dördü de tabanın üstünde.

**Doğrulama:** 931+995+1517 = **3443** doğru / 949+1040+1696 = **3685** toplam → **%93,43** ✓

---

### 2.2 · GERÇEK-DÜNYA KORPUSU 🟢 *(kapı yeşil — iki bulgu taşıyor)*

**Üretilen vaka: 2311 · katalog sızıntısı nedeniyle korpusa GİRMEYEN: 14 · ölçülen: 2297**
*(2297 + 14 = 2311 ✓)*

| Kademe | Toplam | Kabul | Doğru | Netleştirme | Dürüst ret | 🔴 Sessiz-yanlış |
|---|---|---|---|---|---|---|
| K1 | 386 | 295 | 25 | **0** | 360 | **1** |
| K2 | 551 | 151 | 17 | **0** | 511 | **23** |
| K3 | 542 | 147 | 9 | **0** | 515 | **18** |
| K4 | 547 | 248 | 0 | **0** | 547 | 0 |
| K5 | 271 | 259 | 12 | **0** | 259 | 0 |
| **TOPLAM** | **2297** | **1100** | **63** | **0** | — | **42** |

**Doğrulama:** kabul 295+151+147+248+259 = **1100** ✓ · doğru 25+17+9+0+12 = **63** ✓ ·
sessiz-yanlış 1+23+18+0+0 = **42** ✓ — üçü de taban dosyasıyla (`gercek_dunya_baseline.json`)
birebir aynı.

**Gözlem A — `netlestirme` sütunu HER kademede 0.** Kılavuz §7 bunu aracın ilan edilmiş
sınırı olarak kaydediyor: *"`route()` düzeyinde netleştirme ile dürüst ret ayırt edilemez —
tablodaki `0` bir ürün ölçümü değil, aracın sınırı."*

**Gözlem B — ⚠ KURAL 1 İHLALİ · katalog sızıntısı: 14 vaka** (üreteç bunları korpusa
almadı). Kütüğe düşen örnekler:

| Vaka | Sızan terim(ler) |
|---|---|
| `kapanışta bakiye tutuyor mu` | `['bakiye']` |
| `ya 3. çeyrek ile kar şılaştır` | `['kar']` |
| `ort hedef aralıkta ile kar şılaştır` | `['kar']` |
| `2. çey rek toplam brut ölç` | `['brut', 'toplam']` |
| `ya borc? bir de borc?` | `['borc', 'borc']` |
| `hadi mart ayı ile kar şılaştır kıyasla` | `['kar']` |
| `sinav puani en düşük birim 📊` | `['birim', 'düşük', 'puani', 'sinav']` |

---

### 2.3 · EVAL 🟡 *(adım ✓ — üç ölçüt de tabanın ALTINDA)*

**Kaynak: `backend/eval/report.json` (taze) ↔ `backend/eval/baseline.json` (dondurulmuş)**

| Ölçüt | Taban | Ölçülen | Delta |
|---|---|---|---|
| `n` | 129 | 129 | 0 |
| `answered` | 111 | **110** | **−1** |
| `answered_precision` | **1,0** | **0,8727** | 🔴 **−%12,7** |
| `coverage` | **1,0** | **0,991** | **−%0,9** |
| `deterministic_share` | **1,0** | **0,982** | 🔴 **−%1,8** |
| `chip_accuracy` | — | 1,0 | — |

**Güven aralıkları (taze koşum):** `precision_ci95 = [0,7976 · 0,9227]` ·
`coverage_ci95 = [0,9507 · 0,9984]`
**Yol dağılımı:** `by_path = {'intent': 108, 'rule': 2}` → deterministik pay 108/110 = **%98,2** ✓

**Süitin aynı ölçüyü tutan iki kapısı da kırmızı verdi** (bkz. §3, sıra 7-8):
`answered-precision DÜŞTÜ: 87.3% < 100.0%` · `deterministik pay DÜŞTÜ: 98.2% < 100.0%` ·
LLM'e kaçan cevap: `ny-kimyasal-maliyet-renk: source=rule yol=rule`

---

### 2.4 · KONUŞMA SENARYOLARI 🟡 *(adım ✓ — bir sınıf ⊘)*

| Sınıf | Doğruluk | Taban | Verdikt |
|---|---|---|---|
| `gorunum_donusumu` | 5/5 | 4 | ✅ |
| `konu_degisimi` | 5/5 | 4 | ✅ |
| `liste_niyeti` | 5/5 | 4 | ✅ |
| `netlestirme_cevabi` | 1/1 | 1 | ✅ |
| 🟡 **`vqr_kalicilik`** | **0/1** | 0 | ✅ · **⊘ 1** |

**Aracın kendi beyanı:** *"⊘ ÖLÇÜLEMEDİ: vaka ne geçti ne kaldı — ölçüm ön koşulu
sağlanmadı (ör. VQR kalıcılığı için `cube+llm` yolu gerekir)."*
Bu, kılavuz §5'in ilan ettiği **üçüncü hâl**dir: ne geçti ne kaldı, **yeşile yuvarlanmadı**.

---

## 3 · SÜİT — 23 BAŞARISIZ TEST (koşum B, TAM LİSTE)

> Aşağıdaki 23 test **her iki koşumda da** başarısız oldu. Gruplar **belirtiye** göredir,
> nedene göre değil.

### G1 · SQL tarih kolonu — **3 test**

| Test | Ölçülen |
|---|---|
| `test_ask_golden.py::test_clarify_then_period_chip` | `assert 'tarih >=' in "SELECT SUM(uretim_kg) AS toplam_uretim_kg FROM urun_maliyetleri WHERE make_date(yil, ay, 1) >= '2026-01-01'"` |
| `test_ask_golden.py::test_tumu_chipi_tarih_filtresini_kaldirir` | aynı iddia, aynı üretilen SQL |
| `test_ask_golden.py::test_convo_uretim_donem_aylara_gore` | `assert ('cube' == 'cube' and 'tarih >=' in "… make_date(yil, ay, 1) >= '2026-02-05'")` |

### G2 · Katalog genişlemesi — **4 test**

| Test | Ölçülen |
|---|---|
| `test_yeni_kup_kapisi.py::test_KUP_SAYISI_BEYANLA_UYUSUYOR` | **10 yeni küp doğmuş:** `bakim_is_emri` · `butce` · `egitim` · `firsat` · `isg` · `kur` · `maliyet` · `sevkiyat` · `sikayet` · `siparis` |
| `test_sinonim_carpismasi.py::test_YANLIS_CUBE_BUYUMEDI` | **4 yeni sinonim çakışması:** `'agirlik'` isg→parti · `'boya maliyeti'` surdurulebilirlik→maliyet · `'toplam maliyet'` ik→maliyet · `'yedek parca maliyeti'` bakim_is_emri→bakim |
| `test_sinonim_carpismasi.py::test_CEVAPSIZ_RED_DAGILIMI_sabit` | Red dağılımı değişti — ölçülen `{'R1': 126, 'R4': 3, 'R10': 13, 'R9': 2}` ↔ kayıtlı `{'R1': 99, 'R10': 5, 'R9': 2, 'R4': 1}` → **R1 99→126 · R10 5→13 · R4 1→3** |
| `test_auth.py::test_packs_discovery_and_tenant_config_flow` | Pack listesi **5 fazla**; ilk fazla kalem `'butce'` |

### G3 · MDL döngüsel bağımlılık — cube `sikayet` — **3 test**

Üçü de aynı motor hatası:
`WrenError: [INVALID_SQL] Failed to analyze MDL: Error during planning: Cube 'sikayet': circular dependency detected in measure expression`

| Test | Etkilenen alanlar |
|---|---|
| `test_member_sweep.py::test_her_OLCU_gercekten_calisir` | `sikayet.sikayet_adedi` · `sikayet.iade_kg` |
| `test_member_sweep.py::test_her_BOYUT_gercekten_calisir` | `sikayet.musteri_kod` · `sikayet.konu` |
| `test_member_sweep.py::test_her_ZAMAN_BOYUTU_kovalanabiliyor` | `sikayet.acilis_tarihi` |

### G4 · Ölçüm tabanı düştü — **2 test**

| Test | Ölçülen |
|---|---|
| `test_eval_gate.py::test_eval_gate_answered_precision_dusmez` | `answered-precision DÜŞTÜ: 87.3% < 100.0% (baseline)` |
| `test_eval_gate.py::test_eval_gate_deterministik_pay_dusmez` | `deterministik pay DÜŞTÜ: 98.2% < 100.0% (baseline)` · `ny-kimyasal-maliyet-renk: source=rule yol=rule` |

### G5 · `route()` `None` döndürdü — **7 test**

| Test | Ölçülen |
|---|---|
| `test_spesifik_olcu_sahibi.py::test_SPESIFIK_olcu_kisa_kimligi_YENER[sapma yüzdesi]` | `assert None is not None` |
| `…[sapma yuzdesi]` | `assert None is not None` |
| `…[sapma oranı]` | `assert None is not None` |
| `…[sapma orani]` | `assert None is not None` |
| `test_spesifik_olcu_sahibi.py::test_DEGISMEMESI_gerekenler[karlılık-parti-kar_marji_yuzde]` | `'karlılık' cevapsız kaldı (red=R1)` |
| `test_spesifik_olcu_sahibi.py::test_ASK_ZINCIRI_yapisal_cevap_veriyor` | `yapısal cevap yok — source=None` · `cube_query` = `None` |
| `test_spesifik_olcu_sahibi.py::test_YANLIS_typo_onerisi_KAYBOLDU` | `assert None is not None` |

### G6 · Netleştirme önceliği — **1 test**

| Test | Ölçülen |
|---|---|
| `test_netlestirme_onceligi.py::test_ACIKKEN_de_ROUTE_cozdugune_DOKUNMUYOR` | `'bu yıl sapma yüzdesi' kapıya takıldı — route çözmüştü, dokunulmamalıydı` · `assert None == 'enerji_sapma'` |

### G7 · Ortam / mount — **1 test**

| Test | Ölçülen |
|---|---|
| `test_beyanlar_curumesin.py::test_TERS_TUZAK_FAZ_0_15_CI_KAPILARI_AYAKTA` | `+ where False = PosixPath('/.github/workflows').exists` — konteynere yalnız `backend/` bağlı |

### G8 · Diğer — **2 test**

| Test | Ölçülen |
|---|---|
| `test_ask_golden.py::test_konusuz_soru_tahmin_etmez` | `assert (['arıza sayısı', 'iş emri adedi', 'hedef', 'borç', 'eğitim saati', 'elektrik', …] and False)` — `any(...)` = `False` |
| `test_responsive.py::test_SAYFA_PAYI_seritle_BIRLIKTE_donuyor` | ⚠ **yalnız koşum B'de** başarısız oldu |

**G1…G8 toplamı: 3+4+3+2+7+1+1+2 = 23** ✓

---

## 4 · YALNIZ KOŞUM A'DA GÖRÜLEN 90 BAŞARISIZ

### 4.1 · Yetki — `401 / süresi dolmuş token` — **85 test**

Hata imzası **tamamında birebir aynı**:
```
AssertionError: {"detail":"Geçersiz veya süresi dolmuş token"}
assert 401 == 200
  where 401 = <Response [401 Unauthorized]>.status_code
```

| Dosya | Adet |
|---|---|
| `test_sosyal_sinif.py` | **19** |
| `test_sunum_tercihi.py` | **17** |
| `test_takip_ucuncu_sinif.py` | **16** |
| `test_telemetri_yazma_yolu.py` | **11** |
| `test_yol_siniri.py` | **8** |
| `test_vqr_schema_version_gate.py` | 4 |
| `test_typo_onerisi_kapisi.py` | 3 |
| `test_tenant_connections.py` | 3 |
| `test_waterfall.py` | 2 |
| `test_stats.py` | 1 |
| `test_starters_departments.py` | 1 |
| **TOPLAM** | **85** |

**Etkilenen test aileleri** *(örnekler)*: `test_SOSYAL_ifade_SQL_URETMEZ` (16 parametre:
`merhaba` · `selam` · `teşekkürler` · `teşekkür ederim` · `sağol` · `eyvallah` · `günaydın` ·
`iyi çalışmalar` · `görüşürüz` · `tamam` · `peki` · `harika` · `süper` · `çok iyi` ·
`anladım` · `ok`) · `test_KIBAR_veri_sorusu_CEVAPLANIYOR` (3) ·
`test_KALICI_TERCIH_TANINIR` (4) · `test_DOGRU_YAZILMIS_SORU_ONERIYLE_KESILMIYOR` (3)

### 4.2 · `KeyError: 'id'` — **5 test**

| Test |
|---|
| `test_starters_departments.py::test_every_starter_query_routes_to_a_real_cube_answer` |
| `test_stats.py::test_stats_today_computes_llm_free_percentage` |
| `test_tenant_connections.py::test_draft_reflects_real_introspected_schema` |
| `test_tenant_connections.py::test_confirm_writes_real_yaml_files_and_relationships` |
| `test_tenant_connections.py::test_confirm_never_overwrites_existing_cube` |

⚠ Bu beş test §4.1'deki dosyalarla **aynı dosyalarda** yer alır (`test_starters_departments`
· `test_stats` · `test_tenant_connections`) ama **farklı belirti** taşır: `401` değil
`KeyError: 'id'`. Bu yüzden ayrı sayılmıştır — çift sayım yoktur.

**§4 toplamı: 85 + 5 = 90** ✓ *(= yalnız koşum A'da görülen)*

---

## 4B · 🔴 DENEYİM SÜİTİ — **CANLI LLM · TEK TEK KOŞUM**

> Kullanıcı talimatı: *"kontrollü teker teker olacak şekilde deneyim testini LLM ile koş —
> önce Gemini, o dolunca OpenRouter'a (NVIDIA) geç; tek tek gitmezsen limit hızlı patlar;
> thread mantığını ve follow-up'ı işleterek."*

### 4B.1 · Koşum kurulumu

| | |
|---|---|
| Araç | `lab/deneyim.py --live --senaryo <ad>` — **senaryo başına AYRI konteyner** |
| Sağlayıcı zinciri | **`['gemini', 'openrouter']`** — araç kütüğünden birebir doğrulandı |
| Modeller | `gemini-flash-lite-latest` → `nvidia/nemotron-3-ultra-550b-a55b:free` |
| Zincir nasıl kuruldu | Ortam **yalnız** Gemini + OpenRouter anahtarlarıyla üretildi; `auto` zincirinin (`anthropic→gemini→groq→xai→openrouter→ollama`) diğer halkaları **anahtarsız** bırakılarak devre dışı kaldı |
| Anahtar hijyeni | Env dosyası **scratchpad**'de (`chmod 600`), **depoya YAZILMADI** |
| Hız sınırı | `LIVE_BEKLE = 5,0 sn` (tur arası) + **15 sn** (senaryo arası, denetçi eklemesi) |
| Koşum | 15 senaryo · **58 tur** · 18:17:07 → 18:29:36 (**~12,5 dk**) |
| Konteyner hijyeni | `-d` + `--name` + `docker wait` + `docker logs` + `docker rm -f` · paralel koşum **yok** |

⚠ Aracın kendi uyarısı kütükte: **`ürün anahtarı (PAYLAŞIMLI)`** — ayrılmış ölçüm anahtarı
(`DIMA_MEASURE_KEY`, yol haritası FAZ 0.16) **hâlâ yok**.

### 4B.2 · Senaryo bazında sonuç — **15/15**

| # | Senaryo | ✅ | ❌ | ⊘ | Çıkış | gemini | cube | 429 |
|---|---|---|---|---|---|---|---|---|
| 1 | `analist_turu` | 4 | 0 | 0 | 0 | 0 | 3 | 0 |
| 2 | `grafik_ustunde` | 3 | 0 | **1** | 0 | 0 | 4 | 0 |
| 3 | `donem_duzeltme` | 2 | 0 | 0 | 0 | 0 | 4 | 0 |
| **4** | 🔴 **`belirsizlik`** | 2 | **1** | 0 | **1** | 0 | 2 | 0 |
| 5 | `kompozisyon` | 3 | 0 | 0 | 0 | 0 | 3 | 0 |
| 6 | `sosyal_isten_ise` | 3 | 0 | 0 | 0 | 0 | 1 | 0 |
| 7 | `konu_degisimi` | 2 | 0 | 0 | 0 | 0 | 3 | 0 |
| 8 | `atif_ifadesi` | 2 | 0 | **1** | 0 | 0 | 3 | 0 |
| 9 | `geri_donus` | 3 | 0 | 0 | 0 | 0 | 4 | 0 |
| 10 | `eylem_onerisi` | 3 | 0 | 0 | 0 | 0 | 1 | 0 |
| 11 | `liste_niyeti` | 2 | 0 | 0 | 0 | **1** | 0 | 0 |
| 12 | `kapsam_disi` | 2 | 0 | 0 | 0 | **1** | 0 | 0 |
| 13 | `uretim_muduru_sabahi` | 4 | 0 | 0 | 0 | 0 | 3 | 0 |
| **14** | 🔴 **`yazim_hatali_gercek_kullanici`** | 2 | **1** | 0 | **1** | 0 | 4 | 0 |
| 15 | `kiyas_turu` | 3 | 0 | **1** | 0 | 0 | 3 | 0 |
| | **TOPLAM** | **40** | **2** | **3** | **2 kırmızı** | **2** | **38** | **0** |

### 4B.3 · 🔴 İKİ KIRMIZI — sözleşme satırıyla

| Senaryo | İhlal edilen satır | Ölçülen |
|---|---|---|
| **`belirsizlik`** | **`S5·belirsizlik: tahmin yok, soru var`** | `q='bu yıl bakiye'` → **`source=cube`** — doğrudan cevaplandı. `bakiye` hem `cari` hem `mizan` tarafından iddia edilen bir terim; **sistem sormak yerine seçti** |
| **`yazim_hatali_gercek_kullanici`** | **`S2·anlat: ≥3 olgu + anlatı + ≥2 chip`** | Dört tur da `source=cube` ile cevaplandı (`bu yil makina bazinda oee` · `aylik goster` · `en kotusu hangisi` · `bunu yorumla`); **son turda anlatı sözleşmesi karşılanmadı** |

**⊘ üç hücre** (`grafik_ustunde` · `atif_ifadesi` · `kiyas_turu`): ölçüm ön koşulu
sağlanmadı — kusur **değil**, aracın ilan ettiği üçüncü hâl.

### 4B.4 · 🔴 EN ÖNEMLİ ÖLÇÜM — **süit LLM'i neredeyse hiç çalıştırmıyor**

| Ölçüt | Değer |
|---|---|
| Toplam tur | **58** |
| **LLM ile cevaplanan** | 🔴 **2** *(yalnız `liste_niyeti` ve `kapsam_disi`, ikisi de `llm:gemini`)* |
| Deterministik küpten cevaplanan | **38** |
| `rule`'a düşen | **0** |
| **429 / kota aşımı** | 🔴 **0** — hiç görülmedi |
| **OpenRouter (NVIDIA) devri** | 🔴 **HİÇ TETİKLENMEDİ** |

**İki sonuç, ikisi de ham gözlem:**
1. **Zincir doğrulandı ama ikinci halkası ölçülemedi.** Pilot koşumda Gemini fiilen cevap
   üretti (`source=llm:gemini`, 5600 ms) — yani zincir **çalışır durumda**. Ancak 58 turluk
   koşumda kota sınırına **hiç çarpılmadı**, dolayısıyla OpenRouter/NVIDIA yoluna
   **hiç düşülmedi**. Bu yol bu turda **⊘ ÖLÇÜLEMEDİ** sayılmalıdır.
2. **58 turun 56'sı deterministik yoldan geçti.** Süit, tasarımı gereği *konuşma
   mekaniğini* ölçüyor; **LLM yolunun yükünü ölçmüyor**.

### 4B.5 · Bu koşumun ölçmediği — *saklanmıyor*

| Ne | Neden |
|---|---|
| **OpenRouter/NVIDIA yolu** | Kota sınırına çarpılmadı → devir tetiklenmedi |
| **Kota davranışı (429 sonrası)** | Aynı sebep |
| **Zor sorgu × çok tur birleşimi** | Süitin 58 turunun tamamı **kısa ve düz** ifadeler; ağır imla hatası, devrik cümle, bileşik istek **yok**. *(Zor tekil sorgu ölçümü ayrı araçtadır: `gercek_dunya`, 2311 vaka, K1-K5 — bkz. §2.2, orada **42 sessiz-yanlış** ölçüldü.)* |

---

## 4C · 🔴 DENETİM SONDASI — **51 ÇOK-TURLU İNSANİ SENARYO · CANLI LLM**

> Kullanıcı talimatı: *"insani senaryolar üret DB'ye göre… daha komplike ve peş peşe olan
> follow-up tarzı… gelen grafiğe soru sor gibi… 50 tane kurgula veritabanımıza uygun."*
> Ölçüt: *"mesele sadece yanlış değil — **hiç gitmeyenleri** de, **yanlış cevapları** da
> bulmak; **kesin doğru hariç** şüpheli, yanlış, eksik her şey rapora eklenmelidir."*

### 4C.1 · Neden ayrı bir sonda gerekti

| Araç | Neyi ölçüyor | Boşluk |
|---|---|---|
| `lab/deneyim.py` | **konuşma mekaniği** (15 senaryo · 58 tur) | §4B'de ölçüldü: **58 turun yalnız 2'si LLM'e gidiyor**; turlar kısa ve düz |
| `lab/gercek_dunya.py` | **zor tekil sorgu** (2311 vaka · K1-K5 · argo/imla) | **tek turluk** — konuşma yok |
| 🔴 **bu sonda** | **zor sorgu × çok tur** | *ikisinin kesişimi hiçbir araçta ölçülmüyordu* |

**Kurulum:** 51 senaryo · **178 tur** · 23 cube'un **gerçek ölçü/boyut adlarından** türetildi
(`demo/wren-project/cubes` derlenmiş katalog) · 6 persona (`ceo·cfo·uretim·kalite·satis·saha`)
· K1-K5 · sağlayıcı zinciri `['gemini','openrouter']` · tur arası 5 sn · her senaryodan önce
yeniden giriş.

### 4C.2 · 🔴 SONDANIN KENDİ KUSURU — ve raporun neden iki kez yazıldığı

Birinci sınıflandırıcım `satır>0 + cube_query var` → **`DOGRU`** diyordu. Bu yalnızca
*"bir cevap geldi"* demekti; **hangi cube'dan, hangi ölçüyle** geldiğini **ölçmüyordu**.

> **Kullanıcı yakaladı:** *"cevap gelmesi doğru demek değil — küp için de aynı durum vardı,
> testler belki de tüm cevapları doğru sanıyor."*

Ölçüldü: ilk sınıflamada **63 `✅ DOGRU`** vardı. Cube seçimleri açılınca **13 turun
cevabının katalog dışından ya da yanlış cube'dan** geldiği görüldü.
🔴 **`DOGRU` etiketi kaldırıldı.** Yerine gelenler — **hiçbiri "doğru" iddia etmez**:

| Etiket | Anlamı |
|---|---|
| 🟢 `CEVAP` | Cevap geldi · beklenen cube'lardan biri · **doğruluğu KANITLANMADI** |
| 🔴 `YANLIS_CUBE` | Cevap geldi ama **beklenenden başka cube/ölçü** |
| 🔴 `KATALOG_DISI` | Cevap **`adhoc`** cube'undan · yönetişimli katalogda **olmayan** ölçü adıyla |
| 🟠 `SESSIZ_SECIM` | Terimin **2+ meşru sahibi** var; sistem **sormadan seçti** — *yanlış olduğu kanıtlanmadı, **şüpheli*** |
| 🟡 `BOS` | Cevap geldi · **0 satır** |
| 🔵 `NETLES` | Sistem geri sordu |
| ⚪ `RET` | Dürüst ret |
| 🟡 `KAYIP` | Takip turunda `cube_query` **hiç yok** — çapa koptu |

### 4C.3 · DAĞILIM — 178 tur

| Etiket | Adet | Pay |
|---|---|---|
| 🟠 **`SESSIZ_SECIM`** | **50** | **%28,1** |
| 🟢 `CEVAP` *(doğruluğu kanıtlanmadı)* | 43 | %24,2 |
| 🔵 `NETLES` | 43 | %24,2 |
| ⚪ `RET` | 16 | %9,0 |
| 🟡 `BOS` | 10 | %5,6 |
| 🔴 **`KATALOG_DISI`** | **9** | **%5,1** |
| 🔴 **`YANLIS_CUBE`** | **4** | **%2,2** |
| 🟡 `KAYIP` | 3 | %1,7 |
| **TOPLAM** | **178** | |

🔴 **"Kesin doğru" sayılabilecek tur: SIFIR.** En iyi etiket `CEVAP` bile yalnız *"beklenen
cube'lardan biri seçildi"* demektir — **dönen sayının doğruluğu bu sondayla kanıtlanamaz.**

### 4C.4 · 🔴 KIRMIZI — 13 tur

| Senaryo | Soru | Gelen cevap | Olması gereken |
|---|---|---|---|
| **`satis_iade_orani`** ×4 | `iade oranı bu yıl` · `aylara göre` · `en kötü ay` · `o ayda hangi müşteri` | 🔴 **`parti.fire_orani_yuzde`** | `ticaret.iade_orani_yuzde` — **İADE ≠ FİRE.** Dört turun dördü de aynı yanlış ölçüyle |
| **`cfo_yaslandirma`** | `hangi cari` | 🔴 `adhoc.`**`toplam_tolerans_de`** | `vadesi_gecen` · ⚠ `yaslandirma` cube'u bu tenant'ın **derlenmiş kataloğunda YOK**; dönen ölçü bir **renk sapması toleransı** |
| **`kalite_sikayet_zinciri`** | `konu bazında dağılımı` | 🔴 `adhoc.`**`toplam_is_emri_sayisi`** | `sikayet.sikayet_adedi` — **iş emri sayısı** döndü |
| **`ceo_genel`** | `işler nasıl gidiyor` | 🔴 `adhoc.toplam_toplam_siparis` | — |
| **`ceo_nerede_kaybediyoruz`** | `en çok nerede kaybediyoruz` | 🔴 `adhoc.toplam_toplam_sure_dk` | — |
| **`ceo_bu_ay_iyi_mi`** | `hangi alanda kötüleştik` | 🔴 `adhoc.toplam_guncel_kalite` | — |
| **`saha_yazim_agir2`** | `makinelere gore` | 🔴 `adhoc.toplam_toplam_uretim_kg` | `oee`/`parti` |
| **`saha_olumsuz`** | `makine bazında` | 🔴 `adhoc.toplam_toplam_uretim_kg` | ⚠ **dürüst ret bekleniyordu** (olumsuzluk eki) |
| **`sinir_iki_olcu`** | `makine bazında` | 🔴 `adhoc.toplam_toplam_uretim_kg` | ⚠ **dürüst ret bekleniyordu** (§9.2 sınırı) |
| **`sinir_tahmin`** | `bu gidişle yılı nerede kapatırız` | 🔴 `adhoc.toplam_toplam_ciro` | ⚠ **dürüst ret bekleniyordu** — forecast v1'de **YOK** |

**İki gözlem:**
1. `adhoc`'tan gelen **9 cevabın ölçü adları derlenmiş katalogda YOK**. Çift `toplam_toplam_`
   öneki bu adların **otomatik üretildiğini** gösteriyor.
2. 🔴 **Üçü, DÜRÜST RET beklenen turlarda geldi** (`saha_olumsuz` · `sinir_iki_olcu` ·
   `sinir_tahmin`) — sistem *"yapamam"* demek yerine **bir sayı üretti**.

### 4C.5 · 🟠 SESSİZ SEÇİM — 50 tur (%28,1)

Terimin **iki ya da daha çok meşru sahibi** var; sistem **sormadan** birini seçti.
*Yanlış olduğu kanıtlanmadı — ama kullanıcı **hangi tanımın geldiğini bilmiyor**.*

| Terim | Seçilen | Öteki meşru sahip | Senaryo (tur) |
|---|---|---|---|
| `elektrik` | `surdurulebilirlik.toplam_enerji_kwh` | `enerji_makine` | `enerji_elektrik_belirsiz` ×3 |
| `doğalgaz` | `enerji_makine.toplam_dogalgaz_sm3` | `surdurulebilirlik` — ölçü **ikisinde de tanımlı** | `enerji_dogalgaz` ×3 |
| `ciro` | `parti.toplam_ciro` | `ticaret.satis_tutari` — **farklı grain** | `satis_ciro_drill` ×4 · `satis_devrik_uzun` ×2 · `cfo_mali_donem` ×2 · `cfo_eksiltili_donem` ×3 |
| `bakiye` | `mizan.bakiye` | `cari.bakiye` | `cfo_bakiye_belirsiz` ×2 |
| `fire` | `parti.toplam_fire_kg` | `oee.toplam_fire_kg` | `uretim_fire_zinciri` ×4 · `saha_bosluk_hatasi` ×3 · `sinir_grafik_ustu` ×3 |
| `arıza` | `bakim.ariza_sayisi` | `oee.plansiz_durus_dakika` | `uretim_ariza` ×4 |
| `ilk seferde tamam` | `oee.ilk_seferde_tamam_yuzde` | `parti.ilk_seferde_tamam_yuzde` | `uretim_ilk_sefer` ×3 |
| `renk sapması` | `parti.ort_renk_sapmasi` | `kalite.ort_dE` | `kalite_renk_sapmasi` ×4 |
| `enerji maliyeti` | `surdurulebilirlik.toplam_enerji_tl` | `enerji_tesis` | `enerji_maliyet` ×4 |
| `kâr marjı` | `maliyet` / `parti` | ikisi de | `cfo_karlilik` ×2 |
| `eğitim` | `ik`/`egitim` | ikisi de | `ik_egitim` ×3 |

⚠ **`elektrik` özellikle kayda değer:** MIMARI bu vakayı **adıyla** kaydetmiş (*"beklenen
`enerji_makine`, seçilen `surdurulebilirlik`"*) — sonda **aynı seçimi** ölçtü.

### 4C.6 · 🔵 NETLEŞTİRME — hangi senaryolar **hiç cevaplanamadı**

> 🔴 **DÜZELTME — ilk okumam YANLIŞTI.** Bu turları *"Türkçe karakter düşmesi kesiyor"*
> diye yorumlamıştım. Netleştirme **metinleri okununca** görüldü ki hepsi **aynı şeyi**
> söylüyor: **«Hangi dönem için?»** — yani **imla değil, DÖNEM**.

**43 netleştirmenin ayrışması** *(mesaj metni okunarak ölçüldü)*:

| Tür | Adet |
|---|---|
| 🔴 **`Hangi dönem için?`** | **34** |
| — bunların **ilk turda** olanı | 8 *(senaryoda dönem yoktu → **doğru davranış**, ADR-0007-K3)* |
| — 🔴 bunların **TAKİP turunda** olanı | **26** |
| Diğer (ölçü belirsizliği · tanınmayan kelime · konu) | 9 |

🔴 **26 takip turunun tamamında ÖNCEKİ TURDA DÖNEM VARDI.** Örnekler:

| Senaryo | Tur | Soru | Önceki tur |
|---|---|---|---|
| `uretim_oee_dusus` | 3 | `o makinenin duruşları ne kadar` | `bu yıl makine bazında oee` — **dönem vardı** |
| `satis_kanal` | 3 | `hangi kanal önde` | dönem vardı |
| `cfo_karlilik` | 3 | `en kârlı hangisi` | dönem vardı |
| `cfo_mali_donem` | 3 | `fark ne kadar` | dönem vardı |
| `sinir_konu_degisimi` | 2 | `peki ciro ne durumda` | dönem vardı |

**Dokuz "diğer" netleştirmenin metinleri** *(ham)*:

| Senaryo | Soru | Mesaj |
|---|---|---|
| `kalite_iade` | `müşteri bazında` | *"parti için hangi ölçüyü istiyorsun?"* |
| `cfo_butce_sapma` | `gerçekleşme ne kadar` | *"Bütçe / hedef için hangi ölçüyü istiyorsun?"* |
| `cfo_yaslandirma` | `vadesi geçen alacak ne kadar` | *"Birden fazla konu anlaşıldı, hangisini istiyorsun?"* |
| `ceo_bu_ay_iyi_mi` ×2 | `bu ay iyi miyiz` · `geçen ayla kıyasla` | *"Neyi karşılaştırmak/görmek istediğini anlayamadım"* |
| `saha_konusma_dili` | `onun duruşu ne kadar` | 🔴 *"**«onun»** başka bir konu gibi görünüyor. Hangisini istiyorsun?"* |
| `saha_yazim_agir2` | `bu ayki uretim ne kdar` | *"**«kdar»** kısmını anlayamadım"* |
| `saha_olumsuz` | `firesiz partiler kaç tane` | *"parti için hangi ölçüyü istiyorsun?"* |
| `sinir_iki_olcu` | `fire ve rework birlikte` | *"**«birlikte»** kısmını anlayamadım"* |

⚠ **`saha_konusma_dili`'nin mesajı, kullanıcının bildirdiği vakayla (§4C.10) AYNI kalıpta:**
işaret zamiri (`onun`) **bir konu adı sanılıyor**.

### 4C.7 · 🟡 BOŞ SONUÇ — 10 tur

| Senaryo | Sorgu | Ölçülen |
|---|---|---|
| `uretim_vardiya_kiyas` ×4 | `vardiya bazında oee **bu ay**` | `oee.ort_oee × vardiya` — **cube doğru, 0 satır** |
| `uretim_eksiltili` ×3 | `bu ay oee` → `makine` → `en düşük` → `duruş` | ilk tur doldu, **kırılım eklenince boşaldı** |
| `saha_konusma_dili` ×3 | `ya **bu ay** fire ne durumda` | aynı desen |

⚠ **Üçünde de ortak: `bu ay`.** Cevap **sessizce boş** dönüyor; *"bu dönemde veri yok"*
denmiyor.

### 4C.8 · 🟡 ÇAPA KAYBI — 3 tur

`satis_devrik_uzun` (`en iyisi kim peki`) · `cfo_bakiye_belirsiz` (chip tıklaması) ·
`sinir_grafik_ustu` (`peki en düşük ay neydi`) — takip turunda `cube_query` **hiç üretilmedi**.

### 4C.9 · Dile göre desen — 🔴 **imla ≠ sözdizim**

| Dil özelliği | Örnek | Sonuç |
|---|---|---|
| **Devrik cümle** | `oee'yi makine bazında versene bu yıl` | 🟢 **geçti** 3/3 |
| **Tamamı büyük harf** | `BU YIL MAKİNE BAZINDA OEE` | 🟢 **geçti** 3/3 |
| **Boşluk hatası** | `buyıl toplamfire` · `makinebazında` | 🟠 cevap geldi (sessiz seçim) 3/3 |
| ⚠ **Türkçe karakter düşmesi** | `makina bazinda oee ver` | 4/4 netleştirme — **ama sebebi imla DEĞİL, dönem yokluğu** *(bkz. §4C.6 düzeltmesi)* |
| 🔴 **Ağır imla — kelime düzeyinde** | `bu ayki uretim ne **kdar**` | *"«kdar» kısmını anlayamadım"* — **gerçek imla bulgusu** |
| 🔴 **İmla, DÖNEM ifadesinde** | `**bu yl** rewrok kg` | `bu yl` dönem sayılmadı → dönem netleştirmesi |
| 🔴 **Olumsuzluk** | `firesiz partiler kaç tane` | ret yerine **katalog dışı sayı** |

> 🔴 **DÜZELTİLMİŞ SONUÇ:** sözdizimsel zorluk (devrik · büyük harf · boşluk) **sorun
> değil**. İmla **kelime düzeyinde** (`kdar`, `hnagisi`) ve **dönem ifadesinde** (`bu yl`)
> kırıyor. Ama sondanın ölçtüğü **en büyük kırılma imla değil, TAKİP TURUNDA DÖNEM
> KAYBI** (26 tur).

### 4C.10 · 🎁 Kullanıcının bildirdiği vaka

**`personel bazlı verimlilik bu yıl`** → *"«verimlilik» başka bir konu gibi görünüyor.
Hangisini istiyorsun?"*

| Ölçülen | Sonuç |
|---|---|
| `verimlilik` tek başına | ✅ **çalışıyor** — `verim` sinonimiyle `oee.ort_oee` |
| `oee` cube'unun boyutları | `hafta_gunu · hat · makine · vardiya` — **personel boyutu YOK** |
| `parti` cube'unda | `operator · departman · cinsiyet · egitim` **var** |
| MIMARI kaydı | **üç yerde** (`:458` · `:491` · `:997`); davranış **tasarlanmış**: *"«personel» yerine «verimlilikleri» kelimesini işaretliyor — personel kırılımı `parti`de gerçekten VAR, cevaplanamayan şey `verimlilik` ölçüsüdür"* |

**Ham gözlem:** davranış belgelenmiş, **ama mesaj metni yanıltıcı** — *"başka bir konu gibi
görünüyor"* bir **yazım hatası önerisi** gibi okunuyor; söylemek istediği *"bu ölçü ile bu
kırılım aynı cube'da değil"*.

### 4C.11 · 🔴 SONDANIN ÖLÇÜM KUSURU — 77 tur ⊘ (düzeltildi)

İlk koşumda **senaryo 29-51'in tamamı (77 tur) `HTTP 401`** aldı — *"süresi dolmuş token"*.
Sonda **bir kez giriş yapıp ~40 dk koştu**; token yolda süresi doldu.

⚠ **Süit koşum A'daki 85 × 401 ile AYNI İMZA** (§4.1) — iki bağımsız uzun koşum, aynı belirti.

**Düzeltme:** her senaryodan önce yeniden giriş eklendi; 29-51 yeniden koşuldu. Yukarıdaki
178 turluk tablo **düzeltilmiş koşumun** sonucudur.

### 4C.12 · Bu sondanın ölçmediği — *saklanmıyor*

| Ne | Neden |
|---|---|
| **Dönen sayının doğruluğu** | Sonda `cube` ve `ölçü` seçimini ölçer; **rakamın doğruluğunu ölçmez.** Altın cevap ya da `dogrulama_sql` gerekir |
| **`SESSIZ_SECIM`in hangisi doğru** | 50 turda *"sormadan seçildi"* ölçüldü; **seçimin doğruluğu** ölçülmedi — bu bir **sahiplik kararıdır** |
| **OpenRouter / NVIDIA yolu** | 178 turda **429 görülmedi** → devir tetiklenmedi (⊘) |
| **Frontend davranışı** | Sonda `/ask` API'sine gider; **ekranda ne göründüğü** ölçülmedi |

---

## 5 · FRONTEND KAPILARI

### 5.1 · TypeScript 🟢

```
./node_modules/.bin/tsc --noEmit   →  çıkış 0 · 0 satır çıktı
```

### 5.2 · ESLint 🔴 — **5 hata · 5 uyarı** (`✖ 10 problems`)

**Hatalar:**

| # | Dosya:satır | Kural | Metin |
|---|---|---|---|
| 1 | `src/components/FloatingControls.tsx:101:5` | `react-hooks/set-state-in-effect` | *Calling setState synchronously within an effect can trigger cascading renders* |
| 2 | `src/components/GeriAlSeridi.tsx:60:5` | `react-hooks/set-state-in-effect` | aynı |
| 3 | `src/components/KayitBildirimi.tsx:45:55` | `react-hooks/set-state-in-effect` | aynı |
| 4 | `src/lib/odakTuzagi.ts:68:3` | `react-hooks/refs` | *Cannot update ref during render* → `kapatRef.current = kapat;` |
| 5 | `src/components/DcmAkisi.tsx:122:44` | `react/no-unescaped-entities` | `'` kaçırılmamış |

**Uyarılar:**

| # | Dosya:satır | Kural | Metin |
|---|---|---|---|
| 1 | `src/components/InterpretationBar.tsx:194:9` | `no-unused-vars` | `dimToFilter` |
| 2 | `src/components/ResultView.tsx:300:34` | `no-unused-vars` | `_omit` |
| 3 | `src/lib/api-client.ts:27:3` | `no-unused-vars` | `QueryResult` |
| 4 | `e2e/browser-e2e.mjs:134:30` | `no-unused-vars` | `url` |
| 5 | `e2e/browser-e2e.mjs:161:9` | `no-unused-expressions` | — |

---

## 6 · ORTAM

### 6.1 · 🔴 `dima-wren-engine` — 5 gündür çökme döngüsünde

| | |
|---|---|
| Konteyner | `b84deddc0a57_dima-wren-engine` |
| Durum | **`Restarting (1)`** — ~30 saniyede bir |
| Süre | **5 gün** |
| Hata | `java.io.FileNotFoundException: etc/config.properties (No such file or directory)` |
| İz | `io.wren.main.server.Server.doStart(Server.java:51)` ← `io.airlift.bootstrap.Bootstrap.configure(Bootstrap.java:217)` |

**Gözlem:** backend motoru **in-process** kullanıyor
(`backend/app/wren_service.py:1` *"Thin in-process wrapper"* · `:18` `from wren.engine import WrenEngine`).

### 6.2 · Diğer koşan konteynerler *(kayıt için)*

`dima-backend-core` (Up 48 dk) · `dima-qdrant` (5 gün) · `upcyops-minio/redis/postgres` (5 gün) ·
`supabase_*` ×4 (5 gün, healthy)

---

## 7 · YAPISAL KONTROLLER — 🟢 TEMİZ

### 7.1 · Yetim modül

**Ölçüm (AST tabanlı, `app`+`admin_app`+`control_plane` taranarak): 87 modülün 5'i
üretim kodunda hiç import edilmiyor.**

| Modül | Belgedeki kaydı |
|---|---|
| `embed_kapsam` | meşru bekleyiş — **P0-bloke** |
| `sinonim_onerici` | meşru bekleyiş — **tasarım: offline** |
| `kanal_kimlik` | meşru bekleyiş — **adaptör bekliyor** |
| `bayrak_profilleri` | meşru bekleyiş — **test yardımcısı** |
| `main` | ⚠ **yanlış-pozitif** — uvicorn giriş noktası |

**Yeni yetim doğmamış** — `V1-SON-KONTROL` raporunun kaydıyla birebir aynı.

### 7.2 · Bayrak kaydı

`FLAG_REGISTRY` **42** ↔ `demo/packs/features.yml` **41** · YAML'de olup kayıtta olmayan: **0**

Tek fark **`ayni_grain_gocu`** ve gerekçesi kodda yazılı:
*"features.yml'e BİLEREK eklenmedi: bu bir DERLEME-ZAMANI/katalog beyanıdır, tenant-kapsamlı
bir rollout bayrağı değil (FAZ 2.4)."*

### 7.3 · Dondurulmuş tabanlar *(kıyas kaynağı)*

| Dosya | Kayıtlı değer |
|---|---|
| `lab/nl_corpus_baseline.json` | 10.865 tur · `@802b8f5` · ölçüldü 2026-08-02T17:53 |
| `lab/gercek_dunya_baseline.json` | vaka **2297** · kabul **1100** · doğru **63** · sessiz-yanlış **42** |
| `eval/baseline.json` | n **129** · answered **111** · precision **1,0** · coverage **1,0** · det. pay **1,0** |

---

## 8 · DENETÇİNİN KENDİ ÖLÇÜM KUSURLARI

> Kılavuz §9: *"Kapıların kendisi de denetlenir."* Aynı disiplin denetçiye uygulandı.
> **Dört kusur, dördü de bu turda kendi aracımdaydı.**

| # | Kusur | Belirti | Düzeltme |
|---|---|---|---|
| **1** | Süiti **`-n` vermeden** koştum | Tek çekirdek · 19:15 · 20 çekirdeğin 19'u boşta | `backend/CLAUDE.md:166` `pytest -n 8` ile **2:15** ölçmüş; koşum B bunu doğruladı (6:03) |
| **2** | Yetim-modül dedektörüm **regex**'ti, satır başı (`^`) şartı vardı | **29** yetim dedi — fonksiyon içi girintili import'ları kaçırıyordu (`interpret`, `narration_guard` yanlışlıkla yetim göründü) | **AST**'ye çevrildi → gerçek sayı **5** |
| **3** | İlk sınıflamada **12 test "sınıflanamadı"** | Parametreli test adlarındaki unicode kaçışları (`ş`) blok eşleşmesini bozdu | Ön-ek eşleşmesi eklendi; hepsi §4.1'e girdi |
| **4** | İlk kapı koşumunda **`docker … \| tail -40`** | Çıkış kodu `tail`'den geldi (`exit 0` **kapının sonucu değildi**) ve özet boruda kayboldu | Kütük dosyaya yazıldı, çıkış kodu `docker inspect` ile ayrı alındı |

| **5** | **İki koşumun farkını ÇIKARMAYLA hesapladım** (`112 − 23 = 89`) | Küme farkı olduğunu varsaydım; **B'nin A'nın alt kümesi olduğunu doğrulamamıştım**. Gerçekte `test_responsive` **yalnız B'de** başarısız → yalnız A = **90**, yalnız B = **1** | Test **adları kesiştirilerek** yeniden ölçüldü; §1 ve §4 düzeltildi |

> Kusur **4**, kılavuz §3'ün `--rm` yasağıyla **aynı sınıftır**: *"iki koşumun özeti böyle
> kayboldu."*
>
> 🔴 Kusur **5** bu raporun **kendi içindeydi** ve son doğrulama turunda yakalandı.
> Sınıfı: *"iki sayının farkı, iki kümenin farkı değildir."* Rapor yayımlansaydı **89**
> yanlış sayısını taşıyacak ve **B-only olan tek testi** görünmez kılacaktı.

---

## 9 · BU TURDA KOŞULMAYANLAR — *saklanmıyor*

| Ne | Neden |
|---|---|
| ~~`lab/deneyim.py --live`~~ | ✅ **KOŞULDU** — §4B'ye bakınız (15 senaryo · 58 tur · tek tek) |
| **OpenRouter / NVIDIA yolu** | 🔴 **⊘ ÖLÇÜLEMEDİ** — 58 turda 429/kota sınırına hiç çarpılmadı, devir tetiklenmedi |
| **Zor sorgu × çok tur** | Süitin turları kısa ve düz; ağır imla hatası · devrik cümle · bileşik istek **yok** |
| `lab/metamorfik.py --ornek 300` | `--hepsi` kapsamında değil; ayrı tanı aracı |
| `lab/konusma_uretec.py` | aynı |
| `lab/kosut.py` desen kapıları | süit içinde koştu (`test_kosut_deseni.py` ✅) |
| `test_belge_duzeni.py` | **repo kökünden** koşulmalı; konteynerde `git` yok → ⊘ atlanır *(kılavuz §7'de ilan edilmiş)* |
| Frontend `next build` | Bu turda çalıştırılmadı |

---

## 10 · SAYIM DOĞRULAMASI

| İddia | Hesap | Sonuç |
|---|---|---|
| Koşum A toplamı | 112 + 3503 + 25 | **3640** ✓ |
| Koşum B toplamı | 23 + 3605 + 25 + 3 | **3656** ✓ |
| **Küme farkı** *(test adı kesiştirmesiyle)* | ortak **22** · yalnız A **90** · yalnız B **1** | A: 90+22=**112** ✓ · B: 1+22=**23** ✓ |
| §3'ün grup toplamı | 3+4+3+2+7+1+1+2 | **23** ✓ |
| §4'ün toplamı | 85 + 5 | **90** ✓ |
| Gerçek-dünya kabul | 295+151+147+248+259 | **1100** ✓ |
| Gerçek-dünya doğru | 25+17+9+0+12 | **63** ✓ |
| Gerçek-dünya sessiz-yanlış | 1+23+18+0+0 | **42** ✓ |
| Gerçek-dünya vaka | 2297 + 14 sızıntı | **2311** ✓ |
| Korpus doğru-cube | 3443 / 3685 | **%93,43** ✓ |
| eval deterministik pay | 108 / 110 | **%98,2** ✓ |

---

> **BÖLÜM 1 BİTTİ.** Ölçülen çıktı yukarıdadır. Nedenler **BÖLÜM 2**'dedir.

---
---

# BÖLÜM 2 · KÖK NEDEN ANALİZİ

> **Yöntem.** Bölüm 1'in **her bulgusu** bir nedene bağlanmaya çalışıldı. Tikel açıklama
> (*"bu test şu yüzden kırmızı"*) **yeterli sayılmadı**: aranan şey, **birden çok bulguyu
> aynı anda açıklayan** ortak mekanizmadır. Her kök neden **kod/veri kanıtıyla** yazılır;
> kanıtlanamayan **`[DOĞRULANMADI]`** işaretlenir.
>
> 🔴 **Bu bölüm ÇÖZÜM ÖNERMEZ.** Neden ile çözüm ayrı kararlardır; ikincisi kullanıcının.

## 2.0 · ÖZET — yedi kök neden, 178+112 bulgunun tamamını kapsıyor

| # | Kök neden | Kanıt | Açıkladığı bulgular |
|---|---|---|---|
| **KN-1** | 🔴 **Takip turunda DÖNEM çapası kayboluyor** | 43 netleştirmenin **34'ü** dönem sorusu; **26'sı takip turunda** ve **önceki turda dönem VARDI** | Sondanın en büyük tek kümesi · `uretim_oee_dusus` · `satis_kanal` · `cfo_karlilik` · `cfo_mali_donem` · `sinir_konu_degisimi` |
| **KN-2** | 🔴 **Katalog iki katına çıktı, kapılar ve tabanlar büyümedi** | `bf5a7eb`: **+10 cube · +33 tablo · 0 taban/kapı dosyası** | Süitin **4** hatası · **50 sessiz seçim** · `R1` 99→126 · eval precision −%12,7 · gerçek-dünya 42 sessiz-yanlış |
| **KN-3** | 🔴 **İlan edilmiş yetenek sınırı TERMİNAL değil** — Discovery devralıyor | Discovery'nin önündeki tek kapı `yol_siniri` = **kullanıcı tercihi**; **yetenek kapısı yok** | **9 `KATALOG_DISI`** · ret beklenen **3** turda sayı üretilmesi |
| **KN-4** | 🔴 **Ölçüm oturumu ürünün token ömrünü aşıyor** | `control_plane/config.py:38` → `access_ttl_seconds = 15*60` | Süit koşum A'nın **90** hatası · sondanın **77** turu — **ikisi de ⊘, ürün kusuru DEĞİL** |
| **KN-5** | 🔴 **Veri 2026-06-30'da bitiyor; tazelik bayrağı `off`** | `partiler`/`oee_vardiya` `max(tarih)` = **2026-06-30**; bugün **2026-08-05**; `features.yml:134 tazelik: "off"` | **10 `BOS`** tur · *"bu ay"* sorularının sessizce boş dönmesi |
| **KN-6** | 🔴 **Tek satırlık ad çakışması bütün cube'u düşürüyor** | `sikayet/metadata.yml:35` → `iade_kg` ölçüsü `SUM(iade_kg)` — **katalogda tek örnek** | `test_member_sweep` **×3** · `kalite_sikayet_zinciri` · `kalite_iade` · `satis_iade_orani` |
| **KN-7** | 🟡 **İşaret zamiri bir "konu adı" sanılıyor** | *"«onun» başka bir konu gibi görünüyor"* · *"«verimlilik» başka bir konu gibi görünüyor"* — **aynı kalıp** | **3 `KAYIP`** · `saha_konusma_dili` · kullanıcının bildirdiği vaka |

**Kapsama kontrolü:** Bölüm 1'in **112 + 23 + 178 = 313** ölçülen olayının tamamı yukarıdaki
yedi nedenden **en az birine** bağlandı. Bağlanamayan: **§2.1'in `boyahane` hatası**
(`[DOĞRULANMADI]`, §2.8'e bakınız).

---

## 2.1 · KN-1 · 🔴 TAKİP TURUNDA DÖNEM ÇAPASI KAYBOLUYOR

### Ölçüm

| | |
|---|---|
| Toplam netleştirme | **43** |
| — *"Hangi dönem için?"* | **34** (%79) |
| — bunların **ilk turda** olanı | 8 → **doğru davranış** (ADR-0007-K3: dönem eksikse SOR) |
| — 🔴 **takip turunda** olanı | **26** |
| Takipte, **önceki turda dönem var mıydı** | 🔴 **26/26 EVET** |

### Mekanizma

Sonda her takip turunda `cube_query` + `history` **gönderiyor** *(deneyim süitinin kendi
deseni — `lab/deneyim.py:kos()`)*. Cevap `cube_query` taşıyor, cube korunuyor,
**ama dönem filtresi tekrar soruluyor.**

**Kanıt zinciri — `uretim_oee_dusus`:**

| Tur | Soru | Sonuç |
|---|---|---|
| 1 | `bu yıl makine bazında oee` | ✅ `oee.ort_oee × makine` |
| 2 | `en düşük hangisi` | ✅ aynı cube, dönem **korunuyor** |
| 3 | `o makinenin duruşları ne kadar` | 🔵 **«Hangi dönem için?»** |
| 4 | `peki fire tarafı nasıl` | 🔵 **«Hangi dönem için?»** |

**Dönem 2. turu geçiyor, 3. turda kayboluyor.** İkisinin farkı: 2. tur **aynı ölçüyü**
sıralıyor; 3. tur **yeni bir ölçü** istiyor (`duruş`). Yani dönem, **ölçü değişince**
düşüyor.

### Neden bu KÖK neden (tikel değil)

Aynı desen **beş ayrı senaryoda, beş ayrı cube'da** tekrarlıyor
(`oee` · `siparis` · `maliyet` · `ticaret` · konu değişimi) — yani bir cube'un ya da bir
ölçünün kusuru değil, **bağlam taşımanın kendisinin** kusuru.

⚠ Ve etkisi bileşik: dönem sorulunca kullanıcı chip'e tıklıyor → **`Bugün` / `Bu hafta` /
`Bu ay`** öneriliyor → **KN-5** gereği bunların üçü de **boş** dönüyor.

**`[DOĞRULANMADI]`** — dönemin tam olarak hangi kod yolunda düştüğü bu turda **koda inilerek
doğrulanmadı**; ölçüm davranış düzeyindedir.

---

## 2.2 · KN-2 · 🔴 KATALOG İKİ KATINA ÇIKTI, KAPILAR ve TABANLAR BÜYÜMEDİ

### Ölçüm

`bf5a7eb` — *"feat(test ortamı): ERP seed'i 47→80 tablo, katalog 13→23 cube, korpus 15→42 vaka"*

| Ne değişti | Adet |
|---|---|
| Yeni tablo | **33** |
| 🔴 **Yeni cube** | **10** — `bakim_is_emri · butce · egitim · firsat · isg · kur · maliyet · sevkiyat · sikayet · siparis` |
| 🔴 **Güncellenen taban dosyası** | **0** |
| 🔴 **Güncellenen kapı dosyası** | **0** |

### Mekanizma — sinonim uzayı

| Ölçüm | Değer |
|---|---|
| Toplam sinonim terimi | **675** |
| Çakışan terim (2+ cube) | **80** |
| 🔴 **YENİ cube'un ESKİ cube'la çakışması** | **29** |

**Çakışmalar doğrudan Bölüm 1'in bulgularını açıklıyor:**

| Çakışan terim | ESKİ sahip | YENİ sahip | Bölüm 1'deki karşılığı |
|---|---|---|---|
| `iade` · `iade edilen` | `ticaret` | **`sikayet`** | `satis_iade_orani` 🔴 · `kalite_iade` |
| `karlılık` · `kâr marjı` · `marj` · `kar oranı` | `parti` | **`maliyet`** | `cfo_karlilik` 🟠 |
| `bakiye` · `net bakiye` | `cari` | **`yaslandirma`** | `cfo_bakiye_belirsiz` 🟠 |
| `enerji maliyeti` · `boya maliyeti` · `kimyasal maliyeti` | `surdurulebilirlik` | **`maliyet`** | `enerji_maliyet` 🟠 |
| `işçilik maliyeti` | `ik` | **`maliyet`** | — |
| `birim maliyet` · `ortalama maliyet` | `mal`,`ticaret` | **`maliyet`** | — |
| `eğitim` | `parti` | **`egitim`** | `ik_egitim` 🟠 |
| `ağırlık` | `parti` | **`isg`** | süit `test_YANLIS_CUBE_BUYUMEDI` |
| `bakım` · `bakım maliyeti` · `mttr` | `bakim` | **`bakim_is_emri`** | süit aynı test |
| `delta e` · `ortalama sapma` | `kalite` | **`sikayet`** | `kalite_renk_sapmasi` 🟠 |

### Açıkladığı bulgular — tek tek

| Bulgu | Bağlantı |
|---|---|
| `test_KUP_SAYISI_BEYANLA_UYUSUYOR` | Beyan 13 cube, gerçek 23 → **mekanik** |
| `test_YANLIS_CUBE_BUYUMEDI` | Yeni 4 çakışma — hepsi yeni cube kaynaklı |
| `test_CEVAPSIZ_RED_DAGILIMI_sabit` | `R1` 99→**126** · `R10` 5→13 — **R1 = "sahibi belirsiz"**; sahip sayısı arttı |
| `test_packs_discovery_and_tenant_config_flow` | Pack listesi 5 fazla |
| **50 `SESSIZ_SECIM`** | 29 yeni çakışmanın doğrudan sonucu |
| eval `precision` −%12,7 | Taban `bf5a7eb` **öncesinde** donmuş |
| gerçek-dünya **42 sessiz-yanlış** | K2:23 · K3:18 — orta zorlukta yoğunlaşması, terim sahipliği belirsizliğiyle uyumlu |

### Neden bu KÖK neden

Bu **tek commit**, birbirinden bağımsız görünen **yedi ayrı kırmızıyı** aynı anda üretiyor.
Ve commit mesajının kendi ifadesi kritik: *"**test ortamı**"* — yani niyet **ölçüm ortamını
zenginleştirmekti**, ürünün yönlendirme uzayını değiştirmek değil. **Fakat cube eklemek
ikisini birden yapar.**

⚠ **Kılavuzun kendi güvencesi bu sınıfı kapsamıyor:** §4'te *"Genişletme mevcut 47 tabloya
DOKUNMAZ … bir kapı bunu sınıyor (`test_GENISLETME_yalniz_EKLER`)"* yazıyor. Kapı **tablo**
düzeyinde toplamsallığı sınıyor — **cube/sinonim** düzeyinde sınamıyor. *Tablo eklemek
toplamsaldır; çakışan sinonimli cube eklemek **değildir**.*

---

## 2.3 · KN-3 · 🔴 İLAN EDİLMİŞ YETENEK SINIRI TERMİNAL DEĞİL

### Ölçüm

Discovery'ye giden yolda **tek kapı** var (`ask.py:3330`):

```python
if not _yol_izinli("discovery"):
    return _finish(AskResponse(..., note=_yol_siniri_notu("discovery"), ...))
```

Ve `_yol_izinli`'nin kendi belgesi (`ask.py:2360`) üç seviyeyi **kullanıcı tercihi** olarak
tanımlıyor: `"deterministik" | "llm" | None/"kesif"`. 🔴 **Yetenek kapsamına bakan bir kapı
YOK.**

### Mekanizma

```
route()  →  R-kodu ile ret ("forecast yok" · "olumsuzluk" · "iki cube'un ölçüsü")
   ↓        ⚠ bu ret TERMİNAL DEĞİL — yalnız "deterministik yol pes etti"
Intent-JSON  →  boş
   ↓
Discovery  →  LLM ham SQL yazar  →  adhoc cube türetilir  →  BİR SAYI DÖNER
```

Kılavuz §7 bunu zaten **ilan ediyor**: *"`durust_ret` «deterministik yol pes etti» demektir,
«kullanıcı cevapsız kaldı» **değil**; `/ask` orada durmaz."*

🔴 **Bulgu, bu ilanın kendisinde değil — sonucunda:** *"v1'de forecast YOK"* gibi
**ürün-düzeyi bir sınır** da aynı yoldan geçiyor ve **sayıya dönüşüyor**.

### Kanıt — ret beklenen üç tur

| Soru | İlan edilmiş sınır | Gelen cevap |
|---|---|---|
| `bu gidişle yılı nerede kapatırız` | **forecast v1'de YOK** | `adhoc.toplam_toplam_ciro` |
| `firesiz partiler kaç tane` | **olumsuzluk desteklenmiyor** | `adhoc.toplam_toplam_uretim_kg` |
| `fire ve rework birlikte` | **MIMARI §9.2**: iki cube'un ölçüsü aynı sorguda olamaz | `adhoc.toplam_toplam_uretim_kg` |

### Neden bu KÖK neden

Dokuz `KATALOG_DISI` turun **dokuzu da** aynı yoldan geliyor ve **hiçbiri bir cube kusuru
değil** — hepsi *"deterministik yol pes etti, Discovery devraldı"*. Rozet **dürüst kalıyor**
(`source=llm:*`), yani bu bir **halüsinasyon değil**; ama kullanıcı **ilan edilmiş bir
sınırın cevabı yerine bir sayı** görüyor.

⚠ `adhoc` ölçü adlarındaki **çift `toplam_toplam_`** öneki, adların **otomatik üretildiğini**
gösteriyor — yani sayı bir katalog ölçüsüne değil, **o turda doğmuş** bir yapıya ait.

---

## 2.4 · KN-4 · 🔴 ÖLÇÜM OTURUMU ÜRÜNÜN TOKEN ÖMRÜNÜ AŞIYOR

### Ölçüm — tek sayı, iki büyük küme

`control_plane/config.py:38` → **`access_ttl_seconds: int = 15 * 60`** *(15 dakika)*

| Koşum | Süre | 401 | Açıklama |
|---|---|---|---|
| Süit **koşum A** (`pytest`, tek süreç) | **19:15** | **90 test** | 15. dakikadan sonrası |
| Sonda **1. tur** (tek giriş, 51 senaryo) | **~40 dk** | **77 tur** *(senaryo 29-51)* | aynı |
| Süit **koşum B** (`kapi.py --hepsi`, `-n 8`) | **6:03** | **0** | **sınırın altında** |
| Sonda **2. tur** (senaryo başına yeniden giriş) | ~20 dk | **0** | düzeltildi |

### Kanıt

- Hata imzası **tamamında birebir aynı**: `{"detail":"Geçersiz veya süresi dolmuş token"}`
- `KeyError` grubu da aynı kökten: kütükte `KeyError: 'tenant_id'` **401 satırının yanında**
- Koşum B, aynı testleri **6 dakikada** koşuyor ve **hiç 401 almıyor**

### Sonuç — ve bir uyarı

🔴 **Bu bir ÜRÜN kusuru değil, ÖLÇÜM ARACI kusurudur.** Süit koşum A'nın **112 hatasının
90'ı** ve sondanın **77 turu** böylece **⊘ ÖLÇÜLEMEDİ** sayılmalıdır — *hata değil*.

⚠ **Ama tehlikeli yanı bu değil:** 401 alan bir test **kırmızı** verir ve *"ürün bozuk"*
diye okunur. Bölüm 1'in ilk hâlinde tam bu oldu — **112 hata** raporlandı, gerçek **22**.
*Bir kapı, ölçemediği şeyi "başarısız" diye raporlarsa, ölçüm aracının kendisi bir kusur
kaynağıdır* (bu deponun kendi §6.4 kuralı).

---

## 2.5 · KN-5 · 🔴 VERİ 2026-06-30'DA BİTİYOR, TAZELİK BAYRAĞI KAPALI

### Ölçüm

| Tablo | Tarih aralığı | Satır |
|---|---|---|
| `partiler` | **2024-01-01 → 2026-06-30** | 37 878 |
| `oee_vardiya` | **2024-01-01 → 2026-06-30** | 25 806 |

**Bugün: 2026-08-05.** → `bu ay` = **Ağustos** · `geçen ay` = **Temmuz** → **veri YOK**.

`demo/packs/features.yml:134` → **`tazelik: "off"`**

### Mekanizma

```
"bu ay oee"  →  route() ✅ doğru cube + doğru ölçü + doğru dönem filtresi
             →  SQL koşar
             →  0 satır
             →  cevap DÖNER, ama "bu dönemde veri yok" DENMEZ
```

**Cube seçimi doğru, ölçü doğru, filtre doğru — yalnız o aralıkta veri yok.**

### Açıkladığı bulgular

| Senaryo | Turlar | Sorgu |
|---|---|---|
| `uretim_vardiya_kiyas` | 4/4 boş | `vardiya bazında oee **bu ay**` |
| `uretim_eksiltili` | 3/4 boş | `**bu ay** oee` → kırılım eklenince boşaldı |
| `saha_konusma_dili` | 3/4 boş | `ya **bu ay** fire ne durumda` |

### 🔴 KN-1 ile bileşik etki

`KN-1` dönem sorunca sistem **`Bugün` · `Bu hafta` · `Bu ay`** chip'lerini öneriyor.
**Üçü de veri aralığının dışında.** Yani kullanıcı, sistemin **kendi önerdiği** chip'e
tıklayınca **boş sonuç** alıyor.

*Bu, iki ayrı kök nedenin birbirini beslediği tek yer ve Bölüm 1'in en görünür deneyim
kusuru.*

### Bağlam

`§C ölçüt 12 (tazelik)` **bugün 0** — zincir (`SyncState → tazelik.kademe → freshness →
ekran`) `OPERASYON-DURUM.md`'ye göre **bağlandı**, ama **bayrak `off`**. Yani mekanizma var,
**açık değil**.

---

## 2.6 · KN-6 · 🔴 TEK SATIRLIK AD ÇAKIŞMASI BÜTÜN CUBE'U DÜŞÜRÜYOR

### Ölçüm

`demo/packs/**/cubes/sikayet/metadata.yml:35`

```yaml
- name: iade_kg
  expression: SUM(iade_kg)
```

**Ölçünün adı, kendi ifadesindeki kolon adıyla aynı.** Motor hatası:

> `WrenError: [INVALID_SQL] Failed to analyze MDL: Error during planning:
> Cube 'sikayet': circular dependency detected in measure expression`

**Katalog taraması: 23 cube · tüm ölçüler → bu desenin TEK örneği.**

### Etki — bir satır, bir cube

Hata **cube düzeyinde** olduğu için `sikayet`'in **hepsi** düşüyor:

| Düşen | Adet |
|---|---|
| Ölçü | 6 (`sikayet_adedi` · `iade_kg` · `ort_cozum_suresi` · `acik_sikayet` · `agir_sikayet_yuzde` · `ort_sapma_dE`) |
| Boyut | 9 (`musteri_kod` · `konu` · `siddet` · `makine` · …) |

### Açıkladığı bulgular

| Bulgu | Bağlantı |
|---|---|
| `test_member_sweep` ×3 | Doğrudan — ölçü/boyut/zaman-boyutu taraması |
| `kalite_sikayet_zinciri` → `adhoc` | `sikayet` derlenmediği için soru **cube'una ulaşamıyor** → Discovery |
| `kalite_iade` → RET/NETLES | `iade` teriminin **iki sahibinden biri ölü** |
| `satis_iade_orani` → `parti.fire_orani_yuzde` | Aynı: `iade` sahiplerinden `sikayet` ölü, `ticaret` eşleşmedi → benzer sesli başka ölçü |

### Neden bu KÖK neden

**Tek bir YAML satırı**, birbirinden bağımsız görünen **üç süit hatası + üç sonda
senaryosunu** açıklıyor. Ve `KN-2` ile bileşik: `sikayet` **yeni gelen 10 cube'dan biri** —
yani aynı commit hem çakışmayı hem bu kırık cube'u getirdi.

---

## 2.7 · KN-7 · 🟡 İŞARET ZAMİRİ BİR "KONU ADI" SANILIYOR

### Ölçüm — aynı kalıp, üç ayrı yerde

| Kaynak | Girdi | Mesaj |
|---|---|---|
| Sonda `saha_konusma_dili` | `onun duruşu ne kadar` | *"**«onun»** başka bir konu gibi görünüyor. Hangisini istiyorsun?"* |
| 🎁 **Kullanıcının bildirdiği vaka** | `personel bazlı verimlilik bu yıl` | *"**«verimlilik»** başka bir konu gibi görünüyor. Hangisini istiyorsun?"* |
| Sonda `sinir_iki_olcu` | `fire ve rework birlikte` | *"**«birlikte»** kısmını anlayamadım"* |

**Üçünde de aynı yapı:** çözülemeyen bir sözcük **bir konu/ölçü adayı** gibi sunuluyor.

### Mekanizma

`onun` bir **işaret zamiri** (önceki cevaba atıf), `birlikte` bir **bağlaç** — ikisi de
**içerik sözcüğü değil**. Ama çözümleyici bunları *"tanımadığım terim"* kutusuna koyup
**konu netleştirmesi** üretiyor.

⚠ `verimlilik` vakası **farklı ve daha ince**: MIMARI `:458` · `:491` · `:997` bu davranışı
**tasarlanmış** olarak kaydediyor — *"«personel» yerine «verimlilikleri» kelimesini
işaretliyor, çünkü personel kırılımı `parti`de gerçekten VAR, cevaplanamayan şey
`verimlilik` ölçüsüdür."* **Yani teşhis doğru; kusur MESAJIN KENDİSİNDE.**

### Açıkladığı bulgular

**3 `KAYIP`** turu (takip turunda `cube_query` hiç üretilmemesi) + `saha_konusma_dili`'nin
4. turu + kullanıcının vakası.

### Neden bu ayrı bir kök neden

`KN-1` **dönemi** kaybediyor; bu ise **atıf ifadesini** çözemiyor. İkisi de bağlam
kaybı ama **farklı katmanda**: biri filtrenin taşınması, öteki **dilsel gönderimin
çözülmesi**. `sinir_grafik_ustu`'nun `peki en düşük ay neydi` turu ikisini birden gösteriyor.

---

## 2.8 · BAĞLANAMAYAN BULGULAR — `[DOĞRULANMADI]`

> *Bir kök neden analizinin dürüstlüğü, açıklayamadığını söylemesindedir.*

| # | Bulgu | Ne biliniyor | Neden bağlanamadı |
|---|---|---|---|
| **1** | 🔴 **Korpus kapısı `boyahane`: HATA — kıyaslanamadı** | Dokuz dilimin dokuzu da *"tamam"* dedi; `nl_corpus.json`'da `error: None`; kırmızıyı veren **tek kalem** bu | Kütükte ve JSON'da **çelişki var** (biri hata diyor, öteki demiyor). Yeniden ölçüm gerekir |
| **2** | `test_ask_golden` ×3 — `assert 'tarih >=' in "… make_date(yil, ay, 1) >= …"` | `urun_maliyetleri` tablosu `yil`/`ay` kolonlarıyla çalışıyor, `tarih` kolonu yok | Testin beklentisi mi bayat, üretim mi değişti — **koda inilmedi**. ⚠ `urun_maliyetleri` **`bf5a7eb`'in yeni tablosu** → muhtemelen **KN-2** |
| **3** | `test_responsive::test_SAYFA_PAYI_seritle_BIRLIKTE_donuyor` — **yalnız koşum B'de** kırmızı | Koşum A'da hiç görünmedi | Paralel koşumda mı doğuyor, sıraya mı bağlı — ölçülmedi |
| **4** | eval `precision` −%12,7'nin **ne kadarı** KN-2'den | Taban `bf5a7eb` öncesinde donmuş; korelasyon güçlü | **Nedensellik ölçülmedi** — taban tazelenip yeniden koşulmalı |
| **5** | 16 test toplanma farkı (3640 ↔ 3656) | İki koşum farklı sayıda test topladı | Hangi tarafın fazla/eksik topladığı ölçülmedi |
| **6** | ESLint `react-hooks/set-state-in-effect` ×3 | Üçü **aynı sınıf**, üç ayrı bileşende | Ortak bir desen mi (kopyala-yapıştır) yoksa bağımsız mı — **frontend koduna inilmedi** |
| **7** | `dima-wren-engine` çökme döngüsü | `etc/config.properties` yok; **ürüne bağlı değil** (motor in-process) | Konteynerin **kim tarafından, neden** ayakta tutulduğu ölçülmedi |

---

## 2.9 · NEDENLERİN BİRBİRİYLE İLİŞKİSİ

```
          bf5a7eb "test ortamını zenginleştir"
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   +10 cube        +33 tablo      sikayet cube'u
   +29 çakışma     (2026-06'da     iade_kg = SUM(iade_kg)
        │           biten veri)          │
        ▼               │                ▼
   KN-2                 ▼             KN-6
   50 sessiz seçim    KN-5          sikayet ÖLÜ
   4 süit hatası      10 boş tur        │
   R1 99→126             │              ▼
        │                │        iade soruları
        │                │        cube'una ulaşamıyor
        │                │              │
        └────────┬───────┴──────────────┘
                 ▼
        route() çözemiyor / kısmen çözüyor
                 ▼
             KN-3  (yetenek kapısı yok)
        Discovery devralıyor → 9 KATALOG_DISI
                 ▲
                 │
   KN-1 (dönem kaybı) ─── chip önerisi "Bu ay" ──▶ KN-5 (boş sonuç)
                 ▲
                 │
   KN-7 (atıf çözülemiyor) ─── 3 KAYIP

   KN-4 (15 dk token) ── ölçüm aracının kusuru, ürüne DEĞMEZ ── 90+77 tur ⊘
```

**Üç gözlem:**

1. 🔴 **`bf5a7eb` tek başına üç kök nedeni besliyor** (KN-2 · KN-5 · KN-6). Commit'in niyeti
   *"test ortamı"* idi; etkisi **ürünün yönlendirme uzayı, veri aralığı ve katalog
   sağlığı** oldu.
2. 🔴 **KN-1 ile KN-5 birbirini besliyor** — sistem dönem soruyor, önerdiği chip'ler veri
   aralığının dışında. Kullanıcı **kendi ürününün önerisine tıklayıp boş ekran** görüyor.
3. **KN-4 hiçbir ürün bulgusuna değmiyor** — ama Bölüm 1'in ilk hâlinde **112 hatanın
   90'ını** üretti. *Ölçüm aracının kusuru, ürün kusuru gibi raporlanır.*

---

## 2.10 · SINIF DÜZEYİNDE — *tikelden ötesi*

Yedi kök nedeni **daha da yukarı** toplayınca üç sınıf çıkıyor:

| Sınıf | Hangi kök nedenler | Ortak cümle |
|---|---|---|
| **S1 · Toplamsal sanılan değişiklik toplamsal değildi** | **KN-2 · KN-5 · KN-6** | *Tablo eklemek toplamsaldır; **çakışan sinonimli cube eklemek değildir**. Kapı tablo düzeyinde toplamsallığı sınıyor, **anlam düzeyinde sınamıyor**.* |
| **S2 · Bir katmandaki "dürüst ret", bir üst katmanda ret DEĞİL** | **KN-3** | *`route()`'un R-kodu bir **teşhis**tir, bir **karar** değil. Kullanıcıya dönük sınır, kullanıcıya dönük katmanda kapılmalı.* |
| **S3 · Bağlam, filtre düzeyinde taşınıyor ama dil düzeyinde taşınmıyor** | **KN-1 · KN-7** | *`cube_query` turlar arası geçiyor; **dönem** ve **gönderim** geçmiyor. Konuşma bir sorgu zinciri gibi taşınıyor, bir **konuşma** gibi değil.* |
| *(sınıf dışı)* | **KN-4** | Ölçüm aracının kusuru — ürüne değmiyor |

---

## 2.11 · BU ANALİZİN SINIRLARI — *saklanmıyor*

| Sınır | Ne demek |
|---|---|
| 🔴 **Ölçümler `9b2410e`'de alındı; HEAD şimdi `abb74a3`** | Analiz sırasında geliştirici **FAZ 6 kapanış denetimi**ni commit'ledi. **Bulgular bu damgaya aittir**; bir kısmı çoktan düzeltilmiş olabilir |
| 🔴 **Eşzamanlı koşum riski** | Analiz sırasında `tabankorpus` adlı **başka bir test konteyneri** koşuyordu. Kılavuz §3: *"iki test konteyneri ASLA paralel koşmaz — compose kilidi çakışır."* `boyahane` hatası (§2.8/1) bundan etkilenmiş **olabilir** |
| **Nedensellik ≠ korelasyon** | KN-2'nin eval düşüşünü *"açıkladığı"* korelasyondur; **taban tazelenip yeniden koşulmadan** kanıtlanmış sayılmaz |
| **Kod yolu izlenmedi** | KN-1 ve KN-7 **davranış düzeyinde** ölçüldü; hangi fonksiyonda düştükleri **koda inilerek doğrulanmadı** |
| **Sayının doğruluğu hiç ölçülmedi** | Sonda cube/ölçü seçimini ölçtü; **dönen rakamın doğruluğu** hiçbir yerde kanıtlanmadı — bunun için altın cevap ya da `dogrulama_sql` gerekir |
| **50 `SESSIZ_SECIM`in hangisi yanlış** | Ölçülen: *"sormadan seçildi"*. **Seçimin doğru olup olmadığı bir SAHİPLİK KARARIDIR** — mühendislik ölçümü değil |

---

> **BÖLÜM 2 BİTTİ.** Yedi kök neden · üç sınıf · yedi bağlanamayan bulgu.
> **Çözüm ve önceliklendirme bu belgenin kapsamı DIŞINDADIR** — kullanıcı kararıdır.

---
---

# BÖLÜM 3 · KÖK ÇÖZÜMLER

> **Bu bölüm ne yapar.** Bölüm 2'nin yedi kök nedenini, **dışarıdan gelen ikinci bir
> denetim raporuyla** birleştirir ve her kusur **SINIFINI** kapatan mekanizmaları
> **kabul ölçütü biçiminde** yazar.
>
> 🔴 **Bu bölüm KOD YAZMAZ ve uygulama emri DEĞİLDİR.** Denetçi rolü gereği yazılan şey
> *"şöyle düzeltilir"* değil, ***"düzeldiğini şu ölçüm gösterir"***. Sıra ve kapsam
> kararı kullanıcınındır.

## 3.0 · Yöntem — bir düzeltmeyi KÖK ÇÖZÜM yapan üç şart

| Şart | Anlamı | İhlali |
|---|---|---|
| **1 · Sınıf kapatır** | Vaka listesi değil, **değişmez listesi**. Yeni vaka doğduğunda mekanizma onu da kapsar | *"`verdik` kelimesini sözlüğe ekle"* — ADR-0008'in **doğrudan yasakladığı** desen |
| **2 · Tekrarı bir KAPIYA bağlar** | Aynı kusurun bir daha doğmasını **CI engeller**, disiplin değil | Bu depo aynı deseni **üç kez** tek tek düzeltmiş, **kapıya bağlamamış** → her yeni özellik yeniden doğurmuş |
| **3 · Ölçülebilir biter** | Bitip bitmediği **bir sayıyla** görünür | *"iyileştirildi"* — Bölüm 1'in **tamamı** bunun neden yetmediğinin kanıtı |

**Ve dördüncü, negatif şart:** 🔴 *kapsamı açan hiçbir çözüm, sessiz-yanlışı kapatan
çözümden önce inmez.* Gerekçesi §3.2'de **ölçülmüş** durumda: bugün görünür şekilde
reddedilen bir soru, kapsam açılınca **sessiz yanlışa** taşınıyor.

---

## 3.1 · İKİ RAPORUN BİRLEŞTİRİLMESİ

### 3.1a · Neyi ölçtüler, neyi ölçtüm — **örtüşme yok, tamamlama var**

| Katman | **Bu rapor** *(Bölüm 2)* | [**`ANLAMA-KATMANI`**](./2026-08-05_ANLAMA-KATMANI.md) @`bf5a7eb` |
|---|---|---|
| `route()` **anlama** yolu | ⊘ taranmadı | 🔴 **tamamı** — KN-1…KN-10, §14.4 tezi |
| **Takip (follow-up)** yolu | 🔴 **KN-1 — dönem çapası kaybı** | ⊘ **açıkça taranmadı** (kendi K6 körlüğü) |
| **Katalog** sağlığı | KN-2 *(29 yeni↔eski çakışma)* · KN-6 *(dairesel ölçü)* | KN-9 *(55 çarpışma)* · KN-10 *(8 çok-sahipli kelime)* |
| **Merdiven / yetenek sınırı** | KN-3 *(sınır terminal değil)* | KN-7 *("anlamadım" ≠ "yapamıyorum")* |
| **Veri** ekseni | KN-5 *(veri 30.06'da biter, tazelik `off`)* | ⊘ |
| **Ölçüm aracı** | KN-4 *(15 dk token)* | §9 *(alet kendi aynasında ölçüyor)* |
| **Canlı çok-turlu LLM** | 🔴 51 senaryo + deneyim süiti | ⊘ *(sıfır-LLM, tek tur)* |

> 🔴 **İki raporun kör noktaları birbirinin konusu.** Onların **K6**'sı (*"takip yolu,
> `deterministic_refine`, `cross_cube_*` bu raporun dışında"*) bu raporun **KN-1'idir**;
> bu raporun taramadığı `route()` içi ise **onların tamamıdır**. Birleşimleri, ikisinin
> ayrı ayrı gördüğünden fazlasını gösteriyor.

### 3.1b · 🔴 TEK CÜMLELİK ORTAK KÖK — iki raporun on yedi bulgusu

İki listeyi yan yana koyunca **tek bir cümle** on yedi bulgunun on beşini açıklıyor:

> # **BİLGİ VAR — TEMSİL YOK.**
> *Sistem doğru şeyi hesaplıyor, sonra onu tutacak bir nesne olmadığı için **atıyor**.*

| Bulgu | Sistem **neyi biliyordu** | **Neden atıldı** |
|---|---|---|
| KN-1 *(bu rapor)* | Önceki turun **dönem filtresi** | Ölçü değişince `deterministic_refine` **`return None`** — taşıyacak nesne yok |
| KN-3 *(bu rapor)* | *"forecast v1'de yok"* | Yetenek bir **nesne değil**, belge; `route()` ona bakamaz |
| KN-5 *(bu rapor)* | `max(tarih) = 2026-06-30` | `SyncState` `/ask`'e **ulaşmıyor**, `tazelik: "off"` |
| KN-6 *(bu rapor)* | Motor `circular dependency` **teşhis ediyor** | Teşhis **çalışma zamanında**; derleme zamanında tutan kapı yok |
| KN-2 *(bu rapor)* | 29 sinonim çakışması **derleme anında görünür** | Çakışmayı tutan **kapı nesnesi** yok |
| KN-4 *(onlar)* | Sorudaki **kıyas/trend/çok-dönem niyeti** | 🔴 *"Ortada denetlenecek bir **niyet nesnesi yok**"* — kendi cümleleri |
| KN-5 *(onlar)* | `route()` **R9** diyor | Kullanıcı mesajı **ayrı hesaptan** (`partial_unknowns`) geliyor |
| B7 *(onlar)* | `bakiye` → **tam 2 aday, adlarıyla** | `netlestirme_onceligi` `off` → liste **kullanılmıyor** |
| KN-9/10 *(onlar)* | 55 çarpışma + 8 çok-sahipli kelime | `metrik_kaydi` **boş**; karar *"deterministik ama **keyfi**"* |
| KN-2 *(onlar)* | `_covers` `martta`'yı ✅ **doğru biliyor** | `_period_hit_words` **aynı soruyu sormuyor** |

⚠ **Ve dürüst iki istisna** — bunlar temsil değil, **gerçek yokluk**:

| İstisna | Ne eksik |
|---|---|
| **KN-8** *(onlar)* — türetme | `sat‑`→`satış` bilgisi **hiçbir yerde yok**. Çekim (`_ek_gecerli`) var, **türetme yok** |
| **KN-3** *(onlar)* — tek geçiş | İkinci dönem **hiç çıkarılmıyor**; atılan bir bilgi değil, **üretilmeyen** bir bilgi |

> **Bu ayrım çözümü belirler:** *temsil eksikse* → **nesne** eklenir (ucuz, davranış
> değişmez). *Bilgi eksikse* → **yetenek** eklenir (pahalı, ölçülmeli). On yedi bulgunun
> **on beşi** birinci kutuda.

### 3.1c · Ve mimari karşılığı — devralınan raporun tezi **doğrulanıyor ve genişliyor**

Onların §14.4 tezi:

> *"`route()` bir **EŞLEŞTİRİCİ**dir, ama ona **ÇÖZÜMLEYİCİ** işi yaptırılıyor.
> Ürünün tezi (LLM garson, küp aşçı) doğru — ama bugün **garson yok, siparişi aşçı
> alıyor**."*

**Bu tez doğrudur ve bu raporun bulgularıyla bir katman daha genişler:** aynı sıkışma
`route()` içinde değil, **merdivenin her basamağında** var:

| Basamak | Ne olması gerekiyordu | Bugün ne oluyor |
|---|---|---|
| `route()` | eşleştirici | **+ çözümleyici** *(onların tezi)* |
| `deterministic_refine()` | takip düzenleyici | **+ durum taşıyıcı** — ve ölçü değişince taşımayı **bırakıyor** *(KN-1)* |
| Discovery | son çare | **+ yetenek sınırı hakemi** — olmadığı için sınırı **sayıya çeviriyor** *(KN-3)* |
| `compose()` | katman birleştirici | **+ katalog sağlık denetçisi** — ama kapsamı **yalnız G5b** *(KN-2·KN-6)* |

> 🔴 **Genelleştirilmiş tez:** *Bu sistemde her katman, kendinden bir üst soyutlamanın
> işini de yapıyor — çünkü o soyutlama **bir nesne olarak yok**.* İki raporun bütün kök
> nedenleri bu tek cümlenin belirtileridir.

---

## 3.2 · DEVRALINAN RAPORUN BUGÜNKÜ HEAD'DE YENİDEN ÖLÇÜMÜ

> **Neden zorunluydu.** O rapor `bf5a7eb` damgalı; yeniden ölçüm **`abb74a3`**'te
> koşuldu — arada
> **26 commit** var. Ve raporun kendi kuralı şunu emrediyor: *"bir sayı tutmuyorsa
> bulguyu çürütmez — ama **mekanizma ortadan kalkmışsa** bulgu çürür."* Düzelmiş bir
> kusuru çözüm listesine koymak, bu turun yapabileceği **en pahalı hata** olurdu.
>
> ⊙ Ölçüm: `dima-test` · `--network none` · sıfır-LLM · sıfır-DB · katalog **23 cube**
> · `WrenService.schema()` üzerinden *(ilk denemem `mdl.json`'u doğrudan okudu ve
> **kontrol vakası bile düştü** — şema yanlış yüklenmişti; harness düzeltildi).*

### 3.2a · 🔴 AYAKTA KALAN — hepsi, 26 commit sonra

| İddia | `bf5a7eb` | **`abb74a3`** | Durum |
|---|---|---|---|
| **B8 · iki ay KIYAS yerine TOPLANIYOR** | HIT, birleşik tek sayı | 🔴 **AYNEN** — `mart cirosunu subat ile kiyasla` → `parti.toplam_ciro`, filtre **`≥2026-02-01 AND ≤2026-03-31`** | 🔴 **CANLI** |
| **B4 · ay çekimi** | 60/60 düşüyor | 🔴 `martta`·`subata`·`ocaktaki`·`marttan` → **R10**, `period=set()` | 🔴 **AYNEN** |
| **KN-2 · iki sahip** | `_period_hit_words` `\b…\b` | 🔴 `cube_router.py:2081` hâlâ `\b({_MONTH_ALT})\b` | 🔴 **AYNEN** |
| **KN-5 · R10 en sonda** | `:3251` | 🔴 R1…R9 önce, **R10 hâlâ son** (`:3251`) | 🔴 **AYNEN** |
| **B3/B6 · dolgu sözlüğü** | `yaptık`✓ `verdik`✗ | 🔴 `ne kadar fire **yaptik**` → **HIT** · `ne kadar fire **verdik**` → **R10** | 🔴 **AYNEN** |
| **KN-8 · türetme yok** | `sattık`→❌ | 🔴 `ne kadar sattik`·`kim bize ne kadar borclu`·`ne kadar alacagimiz var` → **üçü de R1** | 🔴 **AYNEN** |
| **KÇ-9 · red kayıtlarına bilinmeyen kelime** | yok | 🔴 `interaction_log`'da `uncovered_words` kolonu **hâlâ yok** | 🔴 **AYNEN** |
| **KÇ-0 · niyet nesnesi** | yok | 🔴 `app/`'de `Niyet` sınıfı **yok** | 🔴 **AYNEN** |
| **KÇ-1 · uyum kapısı** | yok | 🔴 `_BREAKDOWN_HINTS` koruması dışında **yok** | 🔴 **AYNEN** |

**Ve bu raporun kendi kök nedenleri de ayakta:** `sikayet/metadata.yml:36` →
`expression: SUM(iade_kg)` **HEAD'de duruyor** (KN-6).

> 🔴 **Sonuç: devralınan raporun hiçbir mekanizması çürümedi.** Sayıları değil, iddiaları
> **birebir** doğrulandı. Bu, o raporu bu raporun **eş-otoritesi** yapar.

### 3.2b · 🔴 YENİ — devralınan raporda OLMAYAN dört bulgu

Yeniden ölçüm, aynı mekanizmaların **görülmemiş** dört yüzünü verdi:

#### YENİ-1 · Kıyas yutması **iki ayla sınırlı değil** — altı ayı da yutuyor

| Soru | Üretilen filtre | Kullanıcının istediği |
|---|---|---|
| `ocak ve haziran ciro karsilastir` | 🔴 **`≥2026-01-01 AND ≤2026-06-30`** | **iki** ay |
| `2025 ve 2026 ciro kiyasla` | 🔴 **filtre YOK** — tüm tarihin toplamı | iki **yıl** |

> Devralınan rapor bunu *"iki dönem toplandı"* diye kaydetmişti. Gerçek **daha geniş**:
> iki uç nokta bir **aralığa** çevriliyor; aradaki **dört ay da** toplama giriyor. Yani
> hata *"iki sayı yerine bir sayı"* değil, **"iki sayı yerine, istenmemiş altı ayın
> toplamı"**.

#### YENİ-2 · 🔴 Aynı niyetin iki kelimesi, iki farklı cevap — **`değişimi` ≠ `trendi`**

⊙ Ölçüldü:

| Soru | `timeDimensions` | Sonuç |
|---|---|---|
| `ciro **trendi** son 6 ay` | `[{tarih, month}]` ✅ | **aylık seri** — doğru |
| `ciro **değişimi** son 6 ay` | 🔴 **`None`** | **tek sayı** — zaman ekseni yutuldu |

> Devralınan rapor `TREND_YUTULDU` sınıfını **saymıştı** (7 vaka) ama bu **çifti**
> göstermemişti. Çift, kanıtı kesinleştiriyor: kusur *"trend anlaşılmıyor"* değil —
> **aynı niyetin bir eşanlamlısı sözlükte var, öteki yok**. Bu, KN-2'nin
> *(aynı kuralın çok sahibi)* **sözlük düzeyindeki dördüncü örneğidir**.
>
> ⚠ Ve borç defterindeki *"«değişim» istenip TOPLAM verildi (CANLI)"* kaydıyla **birebir
> aynı**: vaka olarak görülmüş, **sınıf olarak kapatılmamış**.

#### YENİ-3 · Çok-dönemli soruda **hangi dönem kazanıyor** — ve cevap kötü

| Soru | Üretilen filtre | Ne oldu |
|---|---|---|
| `son 3 ay ve son 6 ay ciro` | **`≥2026-05-05`** | 🔴 **son 3 ay** kazandı; `son 6 ay` **sessizce düştü** |

> Devralınan rapor *"ikinci dönem yutuluyor"* demişti. Ölçüm bunu **keskinleştiriyor**:
> yutulan, **daha geniş** olan. Yani sistem her zaman **daha dar** pencereyi cevaplıyor
> ve kullanıcı **eksik** bir sayıya bakıyor — üstelik `source=cube` rozetiyle.

#### YENİ-4 · 🔴🔴 Çıplak alt-dize taramasının **YANLIŞ-POZİTİF** yüzü — canlı vaka

Devralınan rapor KN-1'i *"iki yönlü hata üretir: kaçırır **ve kazara yakalar**"* diye
tanımlamış, ama **yakalama** tarafına canlı bir örnek verememişti. ⊙ Bulundu:

| Soru | Üretilen sorgu | Kusur |
|---|---|---|
| `zamaninda teslimat orani` | `siparis.zamaninda_teslim_yuzde` · 🔴 **`granularity: month`** | Kullanıcı **tek bir oran** sordu; **aylık seri** geldi |
| `zamanlama ciro` | `parti.toplam_ciro` · 🔴 **`granularity: month`** | aynı |

⊡ Sebep tek satır — `cube_router.py:1488`:

```python
if any(w in q for w in ["aylik", "aylar", "aya gore", "ay bazinda", "trend", "zaman"]):
```

**`zaman` ⊂ `zamanında`** · **`zaman` ⊂ `zamanlama`**. Kelime sınırı yok.

> 🔴 Bu, bu deponun `_covers` docstring'inde **kendi kaydettiği** hata sınıfının
> (`kar ⊂ ankara`, `fire ⊂ firesiz`) **kapatılmamış bir kapıdaki** hâlidir. Ve
> `zamanında teslimat` **uydurma bir cümle değil** — lojistik/sipariş alanının en yaygın
> KPI ifadesidir.

#### YENİ-5 · Devralınan raporun `in q` envanteri **eksik** — 4 değil, **8+**

Onların KÇ-2'si dört sözlük sayıyor (`_BREAKDOWN_HINTS`·`_COMPARE_HINTS`·
`_EXCLUDE_MARKERS`·`_TH_WORDS`). ⊙ Bugün ölçülen:

| Ek olarak çıplak `in q` ile taranan | Satır | Ne kırıyor |
|---|---|---|
| granülarite — `yillik`·`haftalik`·`gunluk`·`aylik`·**`trend`·`zaman`** | `:1479-1488` | 🔴 **YENİ-4'ün kaynağı** |
| üstünlük — `en dusuk`·`en az`·`en kotu`·`en verimsiz` | `:1494` | sıralama yönü |
| üstünlük — `en cok`·`en yuksek`·`en verimli`·`hangisi` | `:1495` | sıralama yönü |
| granülarite negatif kapı — `haftanin gun`·`hafta gunu` | `:1485` | — |
| meta ipuçları — `_META_HINTS` | `ask.py:659` | merdivenin **ilk** basamağı |

> **KÇ-2'nin kapsamı iki katından fazla.** Ve en tehlikelisi (`:1488`) onların
> listesinde **yoktu** — çünkü o satır bir *"hint"* sözlüğü değil, **gömülü bir liste**.
> 🔴 Bu, KÇ-2'nin **grep kapısının** yalnız `_…HINTS` desenini değil, **`in q` kalıbının
> kendisini** yasaklaması gerektiğini gösterir.

---

## 3.3 · DOKUZ KÖK ÇÖZÜM

> **Numaralandırma.** Bu bölüm `KÖK-1…KÖK-9` kullanır. Devralınan raporun `KÇ-0…KÇ-11`'i
> ve bu raporun `KN-1…KN-7`'si **her maddede eşlenir** — hiçbir kaynak kaybolmaz.
>
> Her madde **üç sütun** taşır ve üçü de zorunludur: **neyi kapatır** · **hangi mevcut
> mekanizmayı genelleştirir** *(sıfırdan yazılan iş şüphelidir)* · **hangi ölçüm bittiğini
> gösterir**.

### 3.3.0 · Özet — dokuz mekanizma, on yedi bulgu

| # | Kök çözüm | Kapattığı | Sınıf |
|---|---|---|---|
| **KÖK-1** | 🔴🔴 **NİYET NESNESİ** — çözümleme ile eşleştirme ayrılsın | onların KN-1·2·3·4·5·6 · bu raporun KN-1 | **çatı** |
| **KÖK-2** | 🔴🔴 **UYUM KAPISI** — niyet sorguya taşınmadıysa cevap gitmez | onların KN-4 · 42 sessiz-yanlış · YENİ-1·2·3 | **fail-closed** |
| **KÖK-3** | **BEYANLI KISMİ CEVAP** — cevapla/reddet ikilisine üçüncü seçenek | KÖK-2'nin kapsam riski | **fail-closed** |
| **KÖK-4** | 🔴 **TAKİP TURUNDA TEMSİL SÜREKLİLİĞİ** | 🔴 bu raporun **KN-1** *(26 tur)* — onların **K6 körlüğü** | **temsil** |
| **KÖK-5** | 🔴 **DERLEME-ZAMANI KATALOG KAPISI** | bu raporun KN-2·KN-6 · onların KN-9·KN-10 | **kapı** |
| **KÖK-6** | **YETENEK BEYANI — üç yönlü** | bu raporun KN-3 · onların KN-7 | **dürüstlük** |
| **KÖK-7** | **TEK BİÇİMBİRİM SAHİBİ** | onların KN-1·2·3·8 · YENİ-4·5 | **kapsam açar** |
| **KÖK-8** | 🔴 **KENDİNİ BİLDİREN ÖLÇÜM** | bu raporun KN-4·KN-5 · onların KÇ-9 · §9 | **ölçüm** |
| **KÖK-9** | **TEK TEŞHİS KAYNAĞI + BELİRSİZLİK→CHIP** | onların KN-5·KN-6 · bu raporun KN-7 | **mesaj** |

---

### 🔴🔴 KÖK-1 · NİYET NESNESİ — *çözümleme ile eşleştirme ayrılsın*

**= devralınan raporun KÇ-0.** Bu raporun ölçümleri onu **doğruluyor ve bir katman
genişletiyor** (§3.1c).

| | |
|---|---|
| **Kapattığı** | Onların **KN-1·2·3·4·5·6** *(altısı birden)* + bu raporun **KN-1**. §3.1b'nin *"bilgi var, temsil yok"* cümlesinin **doğrudan çözümü** |
| **Ne** | Soru → **deterministik Türkçe çözümleyici** → `Niyet{ölçü_adayları, dönemler[], kırılımlar[], filtreler[], niyet_türü, üstünlük, bilinmeyenler[]}` → **eşleştirici** → `CubeQuery` |
| **Neden kök** | KN-4 *(uyum denetimi)* **yazılamaz** çünkü karşılaştırılacak iki şey yok. KN-2 *(çok sahip)* **kaçınılmaz** çünkü *"bu bir çekim mi?"* sorusunun sahibi yok. KN-1 *(bu rapor)* **kaçınılmaz** çünkü taşınacak durum bir nesne değil |
| **Neden YETENEK artırır** | Niyet nesnesi **çok dönem · çok ölçü · iki cube** taşıyabilir — bugün `route()`'un **temsil edemediği** her şey. Bu, savunmacı değil **genişletici** tek maddedir |
| **Genelleştirdiği mevcut çekirdek** | `_syn_hit` · `_covers` · `_ek_gecerli` · `_cekimli_token` · `compare_mode` · `_kiyas_spanlari` — **hepsi zaten var**, dağınık. Yeni dilbilim **yazılmıyor**, var olan **tek çatı altına alınıyor** |
| ⊙ **KAPI · Faz 1** | 🔴 `Niyet` üretilir ve **loglanır**; `route()` davranışı **BİREBİR aynı** kalır. Kapı: `nl_corpus --kapi` **%93,43 sabit** · `eval` `+0,0` · süit yeşil. **Sıfır gerileme, tam görünürlük** |
| ⊙ **KAPI · Faz 2** | Tüketiciler **tek tek** taşınır; her taşımada aynı üç kapı. Bir tüketici taşındığında `_period_hit_words`/`_covers` çelişkisi **ölçülerek** kapanır: §3.2a'nın 60 ay çekiminde **60 HIT** |
| ⚠ **Risk** | **Büyük iş.** Ama kademeli inebilir ve Faz 1 **davranış değiştirmez** — geri alma bir bayrak |
| ⚠ **Dürüst uyarı** | Bu madde **bir mimari karardır**, bir düzeltme değil. Maliyeti **kullanıcının kararıdır**; denetçi yalnız *"ötekilerin hepsi bunun altında ucuzlar"* diyebilir |

---

### 🔴🔴 KÖK-2 · UYUM KAPISI — *niyet sorguya taşınmadıysa cevap gitmez*

**= devralınan raporun KÇ-1.** ⊙ Bu turda **canlı doğrulandı** ve kapsamı **büyüdü**.

| | |
|---|---|
| **Kapattığı** | Onların **KN-4**'ün tamamı *(3 sessiz-yanlış sınıfı, 42 vaka)* + **YENİ-1** *(altı ay yutuluyor)* + **YENİ-2** *(`değişimi` ≠ `trendi`)* + **YENİ-3** *(dar pencere kazanıyor)* |
| **Ne** | `route()` bir `CubeQuery` ürettiğinde, dönmeden önce **sorudaki her niyet işaretinin sorguda karşılığı olduğu** denetlensin. Yoksa → **cevap değil** |
| **Neden kök** | Vaka listesi değil **değişmez listesi**. Yeni bir niyet türü eklendiğinde denetimi de eklenir — mekanizma **kendini genişletir** |
| **Genelleştirdiği mevcut çekirdek** | 🔴 **Zaten VAR** — `_BREAKDOWN_HINTS` koruması (`cube_router.py:866`, `:1191`), kodda adı bile *"SESSİZ-YANLIŞ koruması"*. **Sıfırdan yazılmıyor, dörtten yediye genişletiliyor** |
| **Denetlenecek değişmezler** *(en az)* | kıyas · çok-dönem · trend/zaman ekseni · dışlama · kırılım · üstünlük · eşik |
| ⊙ **KAPI** | `mart cirosunu subat ile kiyasla` · `ocak ve haziran ciro karsilastir` · `2025 ve 2026 ciro kiyasla` · `son 3 ay ve son 6 ay ciro` · `ciro degisimi son 6 ay` — 🔴 **beşi de tek birleşik sayı DÖNDÜRMESİN**. Ve bugün doğru çalışanlar (`ciro en yuksek 5 makine` → `order`+`limit`) **bozulmasın** |
| ⚠ **Risk** | 🔴 **Kapsam DARALIR** — bugün cevaplanan bazı sorular netleştirmeye düşer. **KÖK-3 bu riski alır**; ikisi birlikte inmeli |
| 🔴 **Sıra** | **Kapsamı açan hiçbir madde bundan önce inmez.** Gerekçe ölçülü: §3.2a'da `subata gore` bugün **R9 ile görünür şekilde** reddediliyor; kapsam kapısı önce açılırsa aynı cümle `subat ile` varyantının yoluna düşer ve **dürüst ret sessiz yanlışa döner** |

---

### KÖK-3 · BEYANLI KISMİ CEVAP — *üçüncü seçenek*

**= devralınan raporun KÇ-8.**

| | |
|---|---|
| **Kapattığı** | KÖK-2'nin **kapsam daraltma riski** — taşınamayan niyet artık cevabı **öldürmez, etiketler** |
| **Ne** | Bugün iki seçenek var: **cevapla** ya da **reddet**. Üçüncüsü: *"şu kısmını verdim, şu kısmını **veremedim**, nedeni bu."* |
| **Örnek** | `ocak ve haziran ciro karşılaştır` → *"Ocak–Haziran **toplamı** ₺Z. ⚠ **Kıyas yapamadım** — iki dönemi ayrı ayrı istersen…"* |
| **ADR uyumu** | ADR-0008 *"yanlış cevaba güven rozeti takma"* der. **Beyanlı kısmi cevap rozetsizdir** — yasağı çiğnemez, **karşılar** |
| **Genelleştirdiği mevcut çekirdek** | `explain.assumptions` · `note` alanı · `partial_unknowns` — üçü de var |
| ⊙ **KAPI** | 42 sessiz-yanlışın **hiçbiri çıplak `source=cube`** rozeti almasın; hepsi **etiketli** dönsün |
| ⚠ **Frontend borcu** | Bu madde **arka-ön dikey dilimdir**: etiket üretilip **render edilmezse** hiçbir şey değişmez. `AnalysisCanvas`'ın rozet basmadığı **zaten ölçülü** bir kusur — aynı yüzey |

---

### 🔴 KÖK-4 · TAKİP TURUNDA TEMSİL SÜREKLİLİĞİ

> 🔴 **Bu madde devralınan raporda YOKTUR** — kendi **K6** körlüğü olarak yazılı:
> *"Takip yolu, `deterministic_refine`, `cross_cube_*` bu raporun dışında."*
> Bu raporun **KN-1**'i tam olarak orayı ölçtü ve **kod yolunu buldu**.

| | |
|---|---|
| **Kapattığı** | Bu raporun **KN-1** — sondanın **en büyük tek kümesi**: 43 netleştirmenin 34'ü dönem, **26'sı takip turunda ve önceki turda dönem VARDI** |
| ⊡ **Kanıt — tek satır** | `cube_router.py:1112-1113`:<br>`if em and em not in prev.get("measures", []) and swap is None and topn is None:`<br>`    return None  # farklı metrik açıkça isteniyor → yeni sorgu, LLM sınıflandırsın` |
| 🔴 **Mekanizma** | Takip turu **aynı cube'un başka bir ölçüsünü** isteyince `deterministic_refine` **`None`** döner → soru **taze soru** sayılır → `route()` çıplak takip metnini görür (`o makinenin duruşları ne kadar`) → dönem yok → **«Hangi dönem için?»** |
| **Ve kanıtı kesinleştiren ayrıntı** | Dönemi taşıyacak mekanizma **üç satır aşağıda zaten var**: `cq = copy.deepcopy(prev)`. Ölçü-değişimi dalı ona **hiç ulaşmıyor**. 🔴 *Bilgi var, temsil yok — en saf hâli* |
| **Neden ölçü değişince, sıralamada değil** | ⊙ Ölçüldü: tur 2 `en düşük hangisi` *(aynı ölçü + sıralama)* → dönem **korunuyor** ✅ · tur 3 `o makinenin duruşları` *(yeni ölçü)* → dönem **kayboluyor** 🔴. Fark **tam olarak bu daldır** |
| **Yakın komşu — neden yetmiyor** | Hemen üstteki `olcu_ekle` dalı `deepcopy(prev)` **yapıyor** ve filtreleri **koruyor**; ama iki şart istiyor: `olcu_ekleme_takibi` bayrağı *(bugün **`beta`** = açık)* **ve** `_ciplak_olcu_adi(q, …)`. `o makinenin duruşları ne kadar` **çıplak ölçü adı değil** → dala giremiyor → `return None` |
| ⊙ **KAPI** | 3-4 turlu bir thread'de: 1. turda dönem verilir; 2. ve 3. turda **aynı cube'un başka ölçüsü** istenir → 🔴 **dönem netleştirmesi ÇIKMASIN**. Ölçüt: bu raporun 51 senaryosunda **26 takip-dönem netleştirmesi → 0** |
| ⚠ **Ve yanlış çözüm uyarısı** | *"`return None`'ı kaldır"* **yanlış** olurdu: o dal bilinçli — farklı metrik gerçekten yeni bir sorudur. Doğru olan **dönemi soruya değil, OTURUMA bağlamaktır**: ölçü değişse de **dönem çapası** yaşasın. Bu, KÖK-1'in `Niyet` nesnesinin doğal işidir |
| ⚠ **Bağımlılık** | KÖK-1 Faz 2'nin **ilk müşterisi** olmalı — çünkü taşınacak şey bir **durum nesnesidir** |
| ⚠ **Bileşik etki** | 🔴 Bu madde **KN-5 ile kısır döngü** kuruyor: dönem sorulunca `Bugün`/`Bu hafta`/`Bu ay` chip'i öneriliyor, **üçü de veri aralığının dışında** → kullanıcı **kendi ürününün önerisine tıklayıp boş ekran** görüyor. KÖK-4 tek başına bu döngüyü **kırar** |

---

### 🔴 KÖK-5 · DERLEME-ZAMANI KATALOG KAPISI

**= devralınan raporun KÇ-11 + bu raporun KN-2·KN-6.** İki rapor **aynı katmanı iki
ayrı taraftan** buldu.

| | |
|---|---|
| **Kapattığı** | Bu raporun **KN-2** *(29 yeni↔eski sinonim çakışması)* · **KN-6** *(`iade_kg = SUM(iade_kg)` → `sikayet` cube'u ölü)* · onların **KN-9** *(55 çarpışma)* · **KN-10** *(8 çok-sahipli kelime)* |
| **Neden kök** | 🔴 Bugün katalog kusuru **çalışma zamanında** R1 olarak çıkıyor — yani **kullanıcının karşısında**. Bu kapı onu **derleme zamanına** çeker. *Katalog kusuru bir kullanıcı deneyimi olmamalıdır* |
| 🔴 **Genelleştirdiği mevcut çekirdek — ve bu maddenin gücü burada** | ⊡ `app/compose.py:395 _etiket_carpismasi` = **G5b** kapısı **zaten var**: *"üretilen boyutun etiketi mevcut bir boyutun sözlüğünü ÇALIYOR mu?"* — fail-closed, derleme zamanı, kanıtlanmış. **Mekanizma icat edilmiyor; KAPSAMI eksik** |
| **Eksik kapsam — dört denetim** | **(a)** cube-düzeyi sinonim **başka bir cube'un boyut adı** olamaz *(KN-9: 55)*<br>**(b)** ≥2 cube'un sahiplendiği kelime `metrik_kaydi`'nda **yazılı sahip** ister *(KN-10: 8 · bu raporun KN-2: 29)*<br>**(c)** 🔴 ölçü ifadesi **kendi adına referans veremez** *(KN-6 — katalogda tek örnek, bir cube'u tamamen düşürüyor)*<br>**(d)** yeni cube eklenen PR'da **öncesi/sonrası `nl_corpus --kapi`**; doğru-cube gerilerse cube **geri alınır** *(bu raporun KN-2'sinin doğrudan panzehiri)* |
| ⊙ **KAPI** | Mevcut katalogda **55 çarpışma → 0** · `ilgili_cubelar` hiçbir soruda **10 aday** döndürmesin *(bugün `bunu makinelere böl` → 10)* · `SUM(<kendi_adı>)` deseni **derlemeyi kırsın** · `sikayet`'in 6 ölçüsü + 9 boyutu **canlansın** |
| ⚠ **Risk** | **(a)** şıkkı bugünkü katalogda **55 ihlal** bulur — kapı hemen `on` yapılırsa **derleme kırılır**. `off → shadow → on` kademesi zorunlu *(depoda `strict_sql_policy` deseni var)* |
| 💰 **Getiri** | 🔴 **Bu raporun en ucuz maddesi.** (c) şıkkı **tek bir YAML satırını** yakalar ve **3 süit hatası + 3 sonda senaryosunu** birden kapatır |

---

### KÖK-6 · YETENEK BEYANI — *üç yönlü, iki değil*

**= devralınan raporun KÇ-7 + bu raporun KN-3.** İkisi birleşince **üç kutu** çıkıyor;
her iki rapor da ayrı ayrı **iki** kutu görmüştü.

| | |
|---|---|
| **Kapattığı** | Bu raporun **KN-3** *(9 katalog-dışı tur)* · onların **KN-7** *(Vaka 2'nin tamamı)* |
| 🔴 **Üç kutu — bu birleşimin katkısı** | **(1) «Anlamadım»** — kelime tanınmadı *(onların alanı)*<br>**(2) «Yapamıyorum»** — analiz türü yok: ölçü→ölçü etki, mutlak dönem kıyası *(onların alanı)*<br>🔴 **(3) «Yapmıyorum»** — yetenek **v1'de bilinçle yok**: forecast, olumsuzluk, iki cube'un ölçüsü *(bu raporun alanı — **onlarda yok**)* |
| **Neden üçüncü kutu ayrı** | (2) bir **eksiklik**tir, yol haritasına girer. (3) bir **karardır**, girmez. İkisini aynı mesajla vermek, kullanıcıya *"bekle, gelecek"* dedirtir — oysa gelmeyecek |
| 🔴 **Ve KN-3'ün asıl kusuru burada** | Bugün (3) hiçbir yerde **terminal değil**: `route()`'un R-kodu bir **teşhis**, bir karar değil → Discovery devralıyor → *"forecast v1'de yok"* **bir sayıya dönüşüyor** (`adhoc.toplam_toplam_ciro`) |
| **Genelleştirdiği mevcut çekirdek** | `_yol_izinli()` **var** ama bir **kullanıcı tercihi** okuyor (`ask.py:3330`). Aynı kapıya bir **yetenek kapsamı** eklenir — yeni kapı açılmaz |
| ⊙ **KAPI** | `bu gidisle yili nerede kapatiriz` · `firesiz partiler kac tane` · `fire ve rework birlikte` → 🔴 **üçü de SAYI döndürmesin**; *"bunu v1'de yapmıyorum / henüz yapamıyorum"* desin, **hangisi olduğunu belirterek** |
| 💰 **Getiri** | Devralınan raporun ifadesiyle *"**en ucuz, en görünür kazanç**"*. Kullanıcının **boşuna cümle düzeltmesini** bitirir |
| ➕ **Yan çıktı** | (2) kutusunun içeriği, doğrudan **yol haritasının eksik-yetenek listesidir** |

---

### KÖK-7 · TEK BİÇİMBİRİM SAHİBİ

**= devralınan raporun KÇ-2 + KÇ-3 + KÇ-4 + KÇ-10, tek çatı altında.** Dördü de aynı
şeyi söylüyor: *Türkçe kelime kararının **tek bir sahibi** olmalı.*

| Alt-madde | Kapattığı | ⊙ Kapı ölçütü |
|---|---|---|
| **7a · `in q` YASAĞI** *(KÇ-2)* | Onların KN-1 · **YENİ-4** *(`zaman` ⊂ `zamanında`)* · **YENİ-5** | 🔴 Modülde **hiçbir** sözlük `in q` ile taranmasın — **grep testiyle** kilitlenir *(kod-yapısı testi)*. ⚠ Kapsam **8+ yer**, onların saydığı 4 değil |
| **7b · SÖZLÜK→KURAL** *(KÇ-3)* | Onların B3+B6 — `yaptık`✓ `verdik`✗ | §4 probu **≥%90 HIT**, `_STOP_STEMS`'e **tek kelime eklenmeden**. ⊙ Bugün: `ne kadar fire yaptik`→HIT · `ne kadar fire verdik`→R10 |
| **7c · ÇOK-GEÇİŞ** *(KÇ-4)* | Onların KN-3 · **YENİ-3** | `2025 ve 2026 ciro` → **iki dönem** görülsün; `son 3 ay ve son 6 ay` → **ikisi de**. ⊡ `.search` **34**, `.finditer` **10** |
| **7d · TÜRETME** *(KÇ-10)* | Onların KN-8 — `sattık`/`borçlu`/`alacak` | `ne kadar sattik` → `satis_tutari` **ya da** *"tutar mı miktar mı?"* chip'i. 🔴 **Fail-closed**: türetilmiş eşleşme **doğrudan cevap değil, chip** üretsin |
| **7e · AY ÇEKİMİ** *(onların Ö2)* | Onların B4·KN-2 — 60/60 | `martta`·`subata`·`ocaktaki`·`marttan` → **60 çekimde 60 HIT**; `mart ayakkabi` **HIT VERMESİN** *(yanlış-pozitif kapısı)* |

| | |
|---|---|
| **Neden tek madde** | Beşi de **aynı kök nedenin** alt kümesi: *"bu kelime bilinen bir kökün biçimi mi?"* sorusunun **birden çok sahibi var**. Ayrı ayrı düzeltmek, deponun **üç kez** yaptığı ve **her seferinde yeniden doğan** şeydir |
| **Genelleştirdiği çekirdek** | `_syn_hit` · `_covers` · `_ek_gecerli` · `_cekimli_token` — **hepsi var ve doğru çalışıyor**; eksik olan **zorunlu kılınmaları** |
| 🔴 **Sıra** | **KÖK-2'den SONRA.** 7a–7e'nin hepsi **kapsamı açar**; uyum kapısı yoksa açılan kapsam sessiz-yanlışı **yayar** — §3.2a'nın `subata gore` ölçümü bunun kanıtı |
| ⚠ **ADR-0008 sınırı** | 7d **tek riskli olan**: türetme **anlam kaydırabilir** (`al‑`→`alacak` ✓ ama `al‑`→`alıcı` **boyut**). Bu yüzden fail-closed |

---

### 🔴 KÖK-8 · KENDİNİ BİLDİREN ÖLÇÜM

**= devralınan raporun KÇ-9 + bu raporun KN-4·KN-5 + her iki raporun kendi alet
kusurları.** *Bir kapı, ölçemediği şeyi "başarısız" diye raporlarsa, ölçüm aracının
kendisi bir kusur kaynağıdır.*

| Alt-madde | Kapattığı | ⊙ Kapı ölçütü |
|---|---|---|
| **8a · RED KAYITLARI KENDİ BOŞLUĞUNU BİLDİRSİN** *(KÇ-9)* | Sözlük boşluğu **tahminle** değil **ölçümle** kapanır | `interaction_log`'a `uncovered_words` + `aday_cubelar`. Bir haftalık kayıttan *"en sık düşüren 20 kelime"* raporu üretilebilsin. ⊙ Bugün kolon **yok** |
| **8b · TAZELİK `/ask`'e ULAŞSIN** | 🔴 Bu raporun **KN-5** — 10 boş tur | `SyncState.max(tarih)` cevaba **taşınsın**; `tazelik: "off"` → `shadow`. Kapı: `bu ay oee` → **"veri 30.06.2026'da bitiyor"** desin, sessizce **0 satır** dönmesin |
| **8c · CHIP ÖNERİSİ VERİ ARALIĞINA UYSUN** | 🔴 KN-1+KN-5 **kısır döngüsü** | Dönem netleştirmesi `Bugün`/`Bu hafta`/`Bu ay` önerdiğinde, **veri aralığı dışındaki chip gösterilmesin** |
| **8d · ÖLÇÜM OTURUMU ÜRÜN SINIRINI AŞMASIN** | Bu raporun **KN-4** — 90+77 tur ⊘ | Uzun koşan her ölçüm aracı **token yeniler**; ya da kapı, 401'i **hata değil `⊘ ÖLÇÜLEMEDİ`** diye raporlar |
| **8e · TABAN, KATALOGLA BİRLİKTE TAZELENSİN** | Bu raporun **KN-2** | Cube ekleyen PR, `eval/baseline.json` + `nl_corpus_baseline.json`'ı **aynı PR'da** tazelesin **ya da tazelenmediğini YAZSIN**. ⊙ `bf5a7eb`: **0 taban dosyası** |

> 🔴 **8a'nın stratejik değeri en yüksek.** Sözlük boşluğunu **kendini bildiren bir veri
> kümesine** çevirir: *"bu ay 412 soru `sattık` yüzünden düştü."* Böylece katalog kararı
> **ölçüyle** verilir. **Yan kazanç:** elle vaka yazma ihtiyacını azaltır ve devralınan
> raporun §6.3'te teşhis ettiği *"sistemi kendi aynasında ölçme"* tuzağına **yapısal
> olarak** düşemez — çünkü girdi **gerçek kullanıcı cümleleridir**.
>
> ⚠ **Ve bu raporun kendi dersi:** Bölüm 1'in ilk hâli **112 hata** raporladı, gerçek
> **22** idi. 90'ı bir **ölçüm aracı kusuruydu**. 8d olmadan bu tekrar eder.

---

### KÖK-9 · TEK TEŞHİS KAYNAĞI + BELİRSİZLİK→CHİP

**= devralınan raporun KÇ-5 + KÇ-6 + bu raporun KN-7.**

| Alt-madde | Kapattığı | ⊙ Kapı ölçütü |
|---|---|---|
| **9a · TEK TEŞHİS** *(KÇ-5)* | Onların **KN-5** — kullanıcıya **yanlış yer** işaret ediliyor | `red_gerekcesi()` ile kullanıcı mesajı **aynı hesaptan**. R10 kapı sırasında **öne**. ⊙ `mart cirosunu subata gore kiyasla` → gerekçe **R9**, mesaj *"«şubata» anlamadım"* — **çelişiyor**, HEAD'de aynen duruyor |
| **9b · BELİRSİZLİK→CHİP** *(KÇ-6)* | Onların **KN-6**·**B7** — `bakiye` 2 aday **biliniyor**, kullanılmıyor | `netlestirme_onceligi` **≥2 sahipli nüfusta** ölçülsün. ⚠ **Ön koşul: CHIP KALİTESİ ölçülsün** — ⊙ onların §14.2.1'i `en cok nerede kaybediyoruz` → `['isg']` buldu: **kendinden emin ve yanlış** |
| 🔴 **9c · ATIF İFADESİ KONU ADI SANILMASIN** | 🔴 Bu raporun **KN-7** — **onlarda yok** | `onun`·`bunu`·`birlikte` bir **konu adayı** olarak sunulmasın. ⊙ Ölçülen mesajlar: *"«onun» başka bir konu gibi görünüyor"* · *"«birlikte» kısmını anlayamadım"* — ve 🎁 kullanıcının bildirdiği *"«verimlilik» başka bir konu gibi görünüyor"* **aynı kalıp** |

> **9c neden ayrı bir madde:** `onun` bir **işaret zamiri**, `birlikte` bir **bağlaç** —
> ikisi de **içerik sözcüğü değil**. Çözümleyici (KÖK-1) bunları **gönderim** olarak
> çözerdi; eşleştirici ise ancak *"katalogda var mı?"* diye sorabiliyor. 🔴 **Bu, §3.1c'nin
> genelleştirilmiş tezinin en görünür kullanıcı yüzüdür.**
>
> ⚠ `verimlilik` vakası **farklı ve daha ince**: MIMARI `:458`·`:491`·`:997` bu davranışı
> **tasarlanmış** olarak kaydediyor *(personel kırılımı `parti`de VAR; cevaplanamayan
> `verimlilik` ölçüsüdür)*. **Teşhis doğru — kusur MESAJIN KENDİSİNDE.** Bu, 9a ile
> aynı aile: doğru teşhis, yanlış cümle.

---

## 3.4 · SIRA VE BAĞIMLILIK

```
  ┌─ ŞİMDİ · KÖK-1'i BEKLEMEDEN ───────────────────────────────────────────┐
  │  ucuz · bağımsız · yüksek getiri · davranış riski düşük                │
  │                                                                        │
  │  KÖK-5c  ölçü kendine referans veremez ....... 1 YAML satırı, 1 cube   │
  │  KÖK-6   yetenek beyanı (üç yönlü) ........... en görünür kazanç       │
  │  KÖK-8a  red kayıtları kendi boşluğunu yazsın  ölçüm altyapısı, 0 risk │
  │  KÖK-8b  tazelik /ask'e ulaşsın .............. 10 boş turu açıklar     │
  │  KÖK-8d  ölçüm oturumu token yenilesin ....... 90+77 turu geri kazanır │
  │  KÖK-5d  cube ekleyen PR korpus koşsun ....... KN-2'nin panzehiri      │
  └────────────────────────────────────────────────────────────────────────┘
                                   │
  ┌─ FAIL-CLOSED ÖNCE · kapsam AÇMADAN ────────────────────────────────────┐
  │  KÖK-2   uyum kapısı .................. 42 sessiz-yanlış + YENİ-1·2·3  │
  │  KÖK-3   beyanlı kısmi cevap .......... KÖK-2'nin kapsam riskini alır  │
  │  KÖK-5a/b katalog çarpışma kapısı ..... shadow → on                    │
  └────────────────────────────────────────────────────────────────────────┘
                                   │
  ┌─ ÇATI · kademeli, Faz 1 davranış DEĞİŞTİRMEZ ──────────────────────────┐
  │  KÖK-1   NİYET NESNESİ                                                 │
  │     └─ Faz 2'nin İLK müşterisi ▶ KÖK-4 (takipte temsil sürekliliği)   │
  └────────────────────────────────────────────────────────────────────────┘
                                   │
  ┌─ SONRA · KAPSAM AÇANLAR ───────────────────────────────────────────────┐
  │  KÖK-7a  in q yasağı  →  7c çok-geçiş  →  7e ay çekimi                 │
  │            →  7b sözlük→kural  →  7d türetme (fail-closed)             │
  └────────────────────────────────────────────────────────────────────────┘
                                   │
  ┌─ MESAJ / KARAR KALİTESİ ───────────────────────────────────────────────┐
  │  KÖK-9a tek teşhis · 9c atıf ifadesi                                   │
  │  KÖK-9b belirsizlik→chip  ⚠ ÖNCE chip KALİTESİ ölçülsün               │
  └────────────────────────────────────────────────────────────────────────┘
```

### 🔴 Sıranın üç değişmez kuralı

| # | Kural | Ölçülmüş gerekçe |
|---|---|---|
| **1** | **Kapsamı açan hiçbir iş, uyum kapısından (KÖK-2) önce inmez** | ⊙ `subata gore` bugün **R9 ile görünür** reddediliyor; `subat ile` **sessizce toplanıyor**. Kapsam önce açılırsa birinci ikinciye taşınır — **dürüst ret sessiz yanlışa döner** |
| **2** | **Kimlik/sinonim SİLEREK sadeleştirme yapılmaz** | ⊙ Denendi ve ölçüldü: `surdurulebilirlik` kimliğinden ham terimler çıkarıldı → erişim **%64→%56**, 110 sessiz-yanlış kapandı ama **388 cevap kayboldu** *(3,5:1 kötü takas)*. Geri alındı ve **testle korunuyor** |
| **3** | **Ölçüm aleti, ölçtüğü şeyden önce onarılır** | ⊙ Bu raporun kendi tarihi: 112 hata raporlandı, **90'ı alet kusuruydu**. Ve `bf5a7eb` **0 taban** güncelledi → eval −%12,7'nin **nedenselliği bugün kanıtlanamıyor** |

### Tek dilim yapılabilecekse

> **`KÖK-5c` → `KÖK-6` → `KÖK-8a` → `KÖK-2` + `KÖK-3`**
>
> Gerekçe: ilk üçü **ucuz, bağımsız ve ölçüm/dürüstlük altyapısını** kurar; son ikisi
> **bugün canlı olan** sessiz-yanlış sınıfını kapatır ve sonraki her kapsam işini
> **güvenli** hâle getirir. `KÖK-1` bu dilimde **yok** — çünkü o bir mimari karardır ve
> önce ötekilerin ölçümü onun gerekçesini **sayıya çevirir**.

---

## 3.5 · YAPILMAMASI GEREKENLER — *ölçülmüş anti-çözümler*

> Bir kök-neden raporunun en az çözüm kadar değerli yarısı budur: **denenmiş ve
> ölçülerek reddedilmiş** yollar. Bunlar tekrar önerilirse, ölçüm **yeniden** yapılmalıdır.

| # | Anti-çözüm | Neden yanlış | Kanıt |
|---|---|---|---|
| **A1** | *"`verdik`i dolgu sözlüğüne ekle"* | ADR-0008'in **doğrudan yasakladığı** desen. Türkçe fiil kümesi **açık**; sözlük onu kovalayamaz | Depo bu deseni **on dört kez** avlamış |
| **A2** | *"Cube kimliğinden çakışan terimleri sil"* | Erişim **%64→%56**; **388 cevap kaybı**. Kimliği kaldırmak **sahipliği çözmez**, yalnız **zorlamayı kaldırır** | `test_SURDURULEBILIRLIK_kimligi_KORUNUYOR` |
| **A3** | *"Önce kapsam açalım, sessiz-yanlışı sonra kapatırız"* | ⊙ Kapsam açmak, **görünür reddi sessiz yanlışa** taşır | §3.2a `subata gore` ↔ `subat ile` |
| **A4** | *"`return None`'ı (KÖK-4) kaldır"* | O dal **bilinçli** — farklı metrik gerçekten yeni bir sorudur. Kaldırmak **ölçü karışması** üretir | `cube_router.py:1112` yorumu |
| **A5** | *"`consistency_k` uyumunu bir güven eşiğine çevir"* | Araştırma **doğrudan çürütüyor**: *"bir model son derece self-consistent olup yine de **tutarlı biçimde yanlış** olabilir"* | Selective-prediction, 2026 |
| **A6** | *"Türkçe morfoloji kütüphanesi (Zemberek/Zeyrek) ekle"* | ⊙ Üst sınır ölçüldü: **%0,48**. 228 çözülemeyenin **186'sı olumsuzluk eki** ve orada **red DOĞRU** *(`firesiz` = `fire`'ın ZIDDI)* | `lab/golge_spike.py` |
| **A7** | *"Belirsizliği chip'e çevirmeyi hemen aç"* | ⚠ Chip'in **kaynağı** `ilgili_cubelar` ise **kendinden emin ve yanlış** konu önerilir | ⊙ `en cok nerede kaybediyoruz` → `['isg']` |
| **A8** | *"Korpusu kısaltıp daha sık koşalım"* | Payda kırpılırsa korpusun **tek gerçek yakalaması** görünmez olur — o sinyal payda **sabitliğine** dayanır | `gitas` düştü, payda 445→342, doğruluk **YÜKSELDİ** |
| **A9** | *"Sonda 'yeşil' olduğu için o turlar doğru"* | 🔴 **Bu raporun kendi hatası.** İlk sınıflandırıcı `satır>0 + cube_query var` → `DOGRU` diyordu; yeniden sınıflamada **63 yeşilin içinde 13 kırmızı** çıktı | §8, denetçi kusuru #4 |

---

## 3.6 · BU ÇÖZÜMLERİN **KAPATMADIĞI** — dürüst sınırlar

| # | Açık | Neden bu bölümde çözülmüyor | Kim kapatmalı |
|---|---|---|---|
| **1** | 🔴 **Dönen SAYININ doğruluğu** | Her iki rapor da **cube/ölçü seçimini** ölçtü. *"Rakam doğru mu?"* hiçbir yerde kanıtlanmadı | Altın cevap kümesi ya da `dogrulama_sql` — **ayrı iş** |
| **2** | **50 `SESSIZ_SECIM`in hangisi yanlış** | Ölçülen: *"sormadan seçildi"*. Seçimin **doğru olup olmadığı** bir **sahiplik kararıdır**, mühendislik ölçümü değil | KÖK-5b'nin `metrik_kaydi` turu — **alan bilgisi işi** |
| **3** | R1'in %62'sinin **ne kadarı** katalogdan, ne kadarı koddan | Devralınan rapor dört sınıfa ayırdı ama **oranlamadı** | KÖK-8a — gerçek red kayıtları |
| **4** | eval −%12,7'nin **nedenselliği** | Taban `bf5a7eb` öncesinde donmuş; korelasyon güçlü, **nedensellik ölçülmedi** | KÖK-8e sonrası yeniden koşum |
| **5** | `boyahane: HATA — kıyaslanamadı` | Kütük *"hata"* diyor, JSON `error: None` — **çelişki** | Yeniden ölçüm *(eşzamanlı konteyner riski)* |
| **6** | Frontend `set-state-in-effect` ×3 | Üçü aynı sınıf, ortak desen mi bağımsız mı — **frontend koduna inilmedi** | ayrı denetim |
| **7** | `interpret.py` · `answer.py` · `viz.py` · `compose.py` | 🔴 **Her iki raporun da ortak körlüğü.** Devralınan rapor bunu **K6** diye yazmış; bu rapor da taramadı | ayrı denetim |
| **8** | Takip yolunun **geri kalanı** | Bu rapor KN-1'i buldu; `cross_cube_*` · `_try_fresh_intent` **taranmadı** | KÖK-1 Faz 2 |
| **9** | LLM basamağının **çıktı kalitesi** | Kota. Bağlanma durumu denetlendi, **cevap kalitesi** değil | kota penceresinde |

> 🔴 **En önemli sınır 1 numaradır** ve iki raporun **hiçbiri** onu ölçmedi. *Doğru cube +
> doğru ölçü seçmek, doğru sayı vermenin **gerek şartıdır, yeter şartı değil**.*

---

## 3.7 · KAPANIŞ — ne ölçüldü, ne iddia ediliyor

| | |
|---|---|
| **Ölçüm damgası** | Bölüm 1–2: `9b2410e` · Bölüm 3 yeniden ölçümü: `abb74a3` |
| ⚠ **Belge depoya alınırken HEAD** | 🔴 **`b439937`** — *bu rapordaki hiçbir ölçüm bu damgada koşulmadı* |
| **Devralınan rapor** | [`2026-08-05_ANLAMA-KATMANI.md`](./2026-08-05_ANLAMA-KATMANI.md) @`bf5a7eb` — **26 commit önce** |
| **Yeniden ölçülen iddia** | **9** — 🔴 **dokuzu da ayakta** |
| **Yeni bulunan** | **5** *(YENİ-1…YENİ-5)* — hiçbiri devralınan raporda yok |
| **Birleştirilen kök neden** | bu raporun **7** + onların **10** = **17**, tekrarsız |
| **Yazılan kök çözüm** | **9 mekanizma**, 20 alt-madde, **hepsi kapı ölçütlü** |
| **Ölçülmüş anti-çözüm** | **9** |
| **Açık bırakılan** | **9** — saklanmadı |

> ### Üç cümlede
>
> **1.** İki denetim, iki farklı katmandan bakıp **aynı cümleye** vardı: *bilgi var,
> temsil yok.* On yedi bulgunun **on beşi** sistemin doğru şeyi hesaplayıp, onu tutacak
> bir nesne olmadığı için **atmasıdır**.
>
> **2.** Bu yüzden çözümlerin **çoğu yeni yetenek değil, var olan bir mekanizmanın
> KAPSAMINI genişletmektir**: `_BREAKDOWN_HINTS` koruması **dörtten yediye** *(KÖK-2)*,
> G5b kapısı **bir denetimden dörde** *(KÖK-5)*, `deepcopy(prev)` **bir daldan ikiye**
> *(KÖK-4)*. Bunlar ucuzdur — ve ucuz oldukları için **bugüne kadar yapılmamış olmaları
> bir öncelik sorunudur, bir zorluk sorunu değil.**
>
> **3.** Ve tek bir kural her şeyin önünde durur: 🔴 ***kapsamı açan hiçbir iş, sessiz
> yanlışı kapatan işten önce inmez.*** Bu, tercih değil — **ölçülmüş** bir sonuçtur.

---

> **BÖLÜM 3 BİTTİ.** Uygulama, sıra ve kapsam kararı **kullanıcınındır**; bu belge
> yalnız *"düzeldiğini şu ölçüm gösterir"* der.
