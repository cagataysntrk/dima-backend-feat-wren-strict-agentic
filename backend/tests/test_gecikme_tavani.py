"""🔴🔴 `A10`/`P-2` — **GECİKME TAVANI KAPISI.**

## Ölçülen kusur — ve neden görünmedi

`2026-08-09_KAPI-YAVASLAMASI-TESHISI`: kapı **1:50 → 13:00 (7,1×)** yavaşladı.
Paralellik sağlamdı, payda kırpılmamıştı (tersine **+%38**). Yavaşlayan şey **ürünün
kendisiydi**: `/ask` **47 → 177 ms (×3,8)**.

🔴 **Ve bunu gören hiçbir kapı yoktu.** Rapor `E-7`: *"30–85× fark ölçülmüş, bütçeye
çevrilmemiş."* Yavaşlama bir kapı kırmızısı olarak değil, **kapının kendi süresi**
olarak fark edildi — yani ürünün gecikmesi, ölçüm aracının faturasına yazıldı.

> *Ölçülen ama bütçesi olmayan bir sayı, bir gözlemdir; kapıya bağlanana kadar bir
> karar üretmez.*

## Neden yalnız DETERMİNİSTİK yol

Bütçenin sahibi `stats.GECIKME_BUTCESI_MS` ve orada altı yol var. Bu kapı yalnız
**LLM'siz** yolları (`cube`·`vqr`·`rule`·`meta`·`catalog`) sınar, çünkü:

* onlar **ağa çıkmaz** → ölçüm tekrarlanabilir ve kapı bedava koşar;
* `47 → 177 ms` gerilemesi **tam olarak orada** oldu (`cube_router`'da sıfır memoizasyon,
  sıcak yolda 41 yeni modül);
* `llm` yolunun gecikmesi bir **sağlayıcı özelliğidir** — onu bir kapıya bağlamak,
  başkasının sunucusunu kendi kırmızımız yapmak olurdu. Onun yeri canlı curl turudur.

⚠ Tavan bir **hedef değil bir sürpriz kapanıdır** (bütçe sözlüğünün kendi cümlesi):
aşılırsa cevap *«hızlandır»* değil önce *«neden»* olmalıdır.
"""

from __future__ import annotations

import time

import pytest

from app.routers.stats import GECIKME_BUTCESI_MS

#: Deterministik yolu **kesin** tetikleyen sorular (katalog terimleriyle, LLM'siz).
_SORULAR = [
    "bu yıl toplam ciro",
    "bu yıl makine bazında ortalama oee",
    "bu yıl toplam fire kg",
    "geçen yıla göre ciro nasıl değişti",
    "bu yıl aylık ciro",
    "teşekkürler",
    "neler sorabilirim",
]

#: 🔴 Isınma turu ölçüme GİRMEZ: ilk istek şema derlemesi/önbellek doldurma taşır ve
#: onu p95'e katmak, tavanı **ürünün değil ilklendirmenin** hızına bağlardı.
_ISINMA = 2
#: Ölçülen tur sayısı (ısınma dâhil).
_TUR = 8

#: 🔴🔴 **TEK ÖRNEKTEN p95 ÇIKMAZ — ve kapı bunu KENDİ üstünde gösterdi.**
#:
#: İlk yazımda her yol için `n=1` vardı ve kapı `meta`'yı **301 ms ↔ 300 ms bütçe** ile
#: kırmızı verdi. Bu bir bulgu değil **gürültüdür**: bir örnek bir yüzdelik değildir ve
#: böyle bir kapı, ölçtüğü sistemden çok kendi zamanlamasını raporlar.
#:
#: ⚠ Az örnekli bir yol **geçmiş sayılmaz da kalmaz**: `ÖLÇÜLEMEDİ` diye raporlanır.
#: *Ölçülemeyeni geçmiş saymak, ölçmemekten daha yanıltıcıdır* — bu deponun
#: `_yuzdelik`'inde (`None` ≠ `0`) zaten yazılı olan ayrımın aynısı.
_ASGARI_ORNEK = 5


def _p95(v: list[float]) -> float:
    s = sorted(v)
    return s[min(len(s) - 1, int(len(s) * 0.95))]


@pytest.mark.parametrize("_tekrar", [1])
def test_DETERMINISTIK_YOL_BUTCEYI_ASMIYOR(client, _tekrar):
    """🔴 `p95` bütçeyi aşarsa kırmızı — ve mesaj *«neden»* sorusunu sorar."""
    tok = client.post("/auth/login", json={"email": "demo-boyahane@usedima.com",
                                           "password": "dima-demo-1234"})
    baslik = ({"Authorization": f"Bearer {tok.json()['access_token']}"}
              if tok.status_code == 200 else {})

    olcum: dict[str, list[float]] = {}
    for i, soru in enumerate(_SORULAR * _TUR):
        t0 = time.monotonic()
        r = client.post("/ask", json={"question": soru}, headers=baslik)
        ms = (time.monotonic() - t0) * 1000
        if r.status_code != 200 or i < _ISINMA * len(_SORULAR):
            continue
        kaynak = r.json().get("source")
        if kaynak in GECIKME_BUTCESI_MS and kaynak != "llm":
            olcum.setdefault(kaynak, []).append(ms)

    assert olcum, (
        "🔴 hiçbir deterministik yol ölçülemedi — kapı SESSİZCE yeşil olurdu. "
        "Sorular artık route'a düşmüyor olabilir (bu da başlı başına bir bulgudur).")

    az = {k: len(v) for k, v in olcum.items() if len(v) < _ASGARI_ORNEK}
    if az:
        print(f"⚠ ÖLÇÜLEMEDİ (n<{_ASGARI_ORNEK}): {az} — bu yollar yargılanMADI")
    asan = [(k, round(_p95(v)), GECIKME_BUTCESI_MS[k], len(v))
            for k, v in olcum.items()
            if len(v) >= _ASGARI_ORNEK and _p95(v) > GECIKME_BUTCESI_MS[k]]
    assert not asan, (
        "🔴 GECİKME BÜTÇESİ AŞILDI (yol, p95_ms, bütçe, n): " + str(asan) + "\n"
        "  ⚠ Cevap «hızlandır» DEĞİL, önce «neden»: yol mu değişti · sıcak yola yeni "
        "bir modül mü girdi · `consistency_k` mi arttı · önbellek mi düştü?\n"
        "  Ölçülmüş taban: `/ask` 47 → 177 ms (×3,8) — ve o gerileme bir kapı "
        "kırmızısı olarak değil, KAPININ KENDİ SÜRESİ olarak fark edilmişti.")


def test_BUTCE_SOZLUGU_TEK_SAHIP():
    """⚠ İkinci bir tavan kopyası, bir gün ayrışır ve hangisinin geçerli olduğu bilinmez."""
    assert GECIKME_BUTCESI_MS["cube"] > 0 and GECIKME_BUTCESI_MS["llm"] > 0
    for yol in ("cube", "vqr", "rule", "meta", "catalog"):
        assert yol in GECIKME_BUTCESI_MS, f"{yol} bütçesi yok"
