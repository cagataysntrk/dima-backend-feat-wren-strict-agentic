# 🔴 KAPI DEFTERİ — *bir kapının değeri, kaç kez **haklı** kırmızı verdiğidir*

> `A8`. Rapor `§4f`'in kapanış cümlesi: *"Bir ölçüm aracının değeri, kaç kez kırmızı
> verdiğiyle değil, kaç kez **haklı** kırmızı verdiğiyle ölçülür — ve bu depoda o sayı
> **hiç tutulmadı**."*
>
> Bu dosya o sayıyı tutar. **Ekleme yapılır, satır silinmez.**

## Neden bir defter — ve neden otomatik olamaz

Bir kırmızının **haklı** olup olmadığı bir ölçüm değil bir **yargıdır**: aynı düşüş
(`%95,1 → %93,5`) bir gerileme de olabilir, bir devir de. `A4` bu ayrımı artık
otomatik **etiketliyor**, ama etiketin doğru olup olmadığını ancak sonraki olay söyler.

⊙ Bu yüzden defter iki sütun taşır ve ikisi **farklı zamanlarda** doldurulur:
*ne yakaladı* (koşum anında) ve *sonradan haklı çıktı mı* (olay kapandığında).

> *Kendi geçmişini tutmayan bir kapı, her seferinde ilk kez konuşuyormuş gibi dinlenir.*

---

## Tally

| | korpus (`--tam`) | tam süit | `eval.run` | konuşma senaryoları |
|---|---|---|---|---|
| ✅ **haklı kırmızı** | **2** | **4** *(2026-08-10)* | 0 | 0 |
| 🔴 **haksız kırmızı** *(yanlış karar verdirdi)* | **1** | 0 | 0 | 0 |
| ⏱ koşum başına maliyet | 1:57 → **13:00** | ~7 dk | ~1,5 dk | ~1,5 dk |

🔴 **Ve bu tablo raporun `§4f` teşhisini KISMEN çürütüyor.** Rapor *"tam süit: birkaç —
aynı kusurları seviye 1 de yakaladı"* diyordu. **2026-08-10'da süit 4 haklı kırmızı
verdi ve dördü de seviye 1'in görmediği sınıflardandı** (aşağıda). Yani süitin değeri
o gün ölçüldüğünde düşük görünmüştü; bugün ölçüldüğünde değil.

*Bir aletin değeri, ölçüldüğü güne aittir; bir kez ölçülüp kapatılan bir hüküm değil.*

---

## Kayıtlar

### 2026-08-04 · korpus · ✅ HAKLI

`gitas` compose yarışıyla korpustan **tamamen düştü**; payda **445 → 342** inerken
doğruluk **%93,2 → %94,3 ÇIKTI**. Sistem bozulurken sayı **iyileşti**.
⚠ Süit · `eval` · senaryolar **üçü de yeşildi** — bu kusuru başka hiçbir şey göremezdi.
**Eksen:** payda (kapsam).

### 2026-08-06 · korpus · ✅ HAKLI

`§EB/A` (`18c90c8`): `sessiz_yanlis` **12 → 18**. Kapsam değişikliğiydi ve kapsamın
ölçüsü korpustur. Değişiklik geri alındı, doğru karar.
**Eksen:** sessiz-yanlış.

### 2026-08-?? · korpus · 🔴 HAKSIZ — *ve faturası bir yeteneğin geri alınması oldu*

`G3` (*"cevapsız dal cevaplı yolu kesemez"*): korpus **%95,1 → %93,5** dedi, değişiklik
**geri alındı**. Düşüş **(b) sınıfıydı** — route çekilmiş, tur garsona devredilmişti ve
üretimde orada gerçek bir LLM var. Yani düşüş bir **kazançtı**.
🔴 **Sorulmadı.** `(a)/(b)` ayrımı o tarihte yoktu; `A4` tam olarak bunun için yazıldı.
**Eksen:** doğruluk yüzdesi — ve o eksen `E-2` ile **veto yetkisini kaybetti**.

### 2026-08-10 · tam süit · ✅ HAKLI ×4 *(hepsi aynı turda, hepsi benim kusurum)*

| # | kapı | ne yakaladı | seviye 1 görür müydü |
|---|---|---|---|
| 1 | `test_COZULMEYEN_ISIM_YOK` | `diyalog.py`'de `datetime` çözülemiyordu — o satır koştuğu an `NameError` | 🔴 **hayır** (statik ad çözümü) |
| 2 | `test_KAPI_kirmizi_VEREBILIR_dekor_degil` | 🔴🔴 **`A4`'ü kurarken kapının kırmızı verme yeteneğini bozmuşum**: eski şemalı tabanda `sessiz_yanlis` 0→7 artarken kapı **yeşil** veriyordu | 🔴 **hayır** — ve bu, kapının *kendi kendini* koruduğu tek satır |
| 3 | `test_modul_buyume` | `ask()` tavanı — ve *"tavanı yükseltme, modüle çıkar"* dedi; `B9` uygulaması `diyalog.py`'ye taşındı, `ask()`te 20 satır yerine **2** kaldı | 🔴 hayır |
| 4 | `test_uc_yetim_degil` | `/stats/plan` + `/stats/katalog` yetim uçtu — `API_ONLY` beyanı gerektirdi | 🔴 hayır |

⊙ **İkincisi bu defterin en değerli satırıdır:** ölçüm altyapısını iyileştirirken
**ölçüm altyapısını bozdum**, ve bunu yakalayan şey o altyapının kendi kapısıydı.
*Kırmızı veremeyen bir kapı bir dekordur* kuralı, kuralı yazanı yakaladı.

### 2026-08-10 · `A10` gecikme tavanı · ✅ HAKLI *(kurulduğu ilk koşumda)*

`meta` p95 **320 ms** · `catalog` **401 ms** (bütçe 300). Bütçenin kendi yorumu *"sabit
metin"* diyordu. Sebep yol değil **önündeki boru hattı**: bir selamlaşma bile şema +
`route()` + niyet zincirinin tamamını ödüyor.
**Eksen:** gecikme — ve bu eksen o güne kadar **hiç ölçülmüyordu**.

### 2026-08-10 · `eval.run` · ⚪ NÖTR

`ny-dE-musteri` `answer → chip`. Ölçüldü ve **devir** olduğu görüldü: route çekildi,
garson `kalite.ort_dE` ile **doğru** cevapladı. `A4`'ün sınıfı; geri alınmadı.
⚠ Bu satır bir *"haksız kırmızı"* değil çünkü kırmızı **vermedi** (tolerans içinde) —
ama vermiş olsaydı `G3`'ün tekrarı olurdu.

---

## Nasıl eklenir

Bir kapı koşumu kırmızı verdiğinde **aynı gün** bir satır açılır: *hangi kapı · ne
yakaladı · hangi eksen · seviye 1 görür müydü*. **Haklı/haksız sütunu boş bırakılır**
ve olay kapandığında (düzeltme kabul edildi ya da geri alındı) doldurulur.

⚠ Boş bırakılan bir yargı bir eksiklik değil, **henüz bilinmeyen** bir şeydir — ama
sonsuza kadar boş kalırsa o kapı hakkında hiçbir şey öğrenilmemiş demektir.
