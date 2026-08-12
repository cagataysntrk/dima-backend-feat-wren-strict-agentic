"""🔴🔴 `§E7` — AYRIŞTIRMAMIZ **LMDI DEĞİL**; toplamsaldır ve **tam toplanabilirdir**.

## Kartın iddiası ve ölçüm

> `§E7`: *«Bugünkü ayrıştırmamız **LMDI-II** ailesinde: artık sıfır ✅, sıra bağımsız ✅ —
> ama **alt-grup toplanabilirliği YOK**… Ve `ln(0)` tanımsız, negatifte LMDI tanımsız.»*

⟳ **ÖLÇÜLDÜ (2026-08-12) — ÖNCÜL YANLIŞ.** `contribution.contributions()` şunu yapıyor:

    delta_i   = simdi_i − onceki_i
    net_pay_i = delta_i / Σ delta × 100

Bu **saf toplamsal fark ayrıştırmasıdır**; gövdede **logaritma yoktur** (`math.log2`
yalnız `§E2`'nin Jensen-Shannon sürprizinde, ayrı bir fonksiyonda).

| kartın kaygısı | ölçüm |
|---|---|
| `ln(0)` tanımsız | ⊘ **konu dışı** — logaritma kullanılmıyor |
| negatifte LMDI tanımsız | ⊘ **konu dışı** — çıkarma her işarette tanımlı |
| alt-grup toplanabilirliği **YOK** | 🔴 **TERSİ**: toplamsal ayrıştırma **tam toplanabilirdir** — parçaların toplamı bütünün farkına **birebir** eşittir |

⊙ LMDI-I ↔ LMDI-II ayrımı **çarpımsal/indeks** ayrıştırma için tanımlıdır (bir değişimi
*etkinlik × yapı × yoğunluk* gibi **çarpanlara** böldüğünde). Biz bir değişimi **tek bir
boyutun segmentlerine** bölüyoruz — başka bir problem.

> *Bir yöntemi ait olmadığı ailenin kusurlarıyla eleştirmek, çözdüğü sorunu göremeden
> onu değiştirmeye çalışmaktır.*

⚠ **Tek gerçek «toplam %100 değil» etkisi bir SUNUM kararıdır** ve makbuzu var: gürültü
payının altındaki segmentler kırpılır ve kırpma **sayısıyla + eşiğiyle** beyan edilir
(`kirpilan_segment` · `kirpilan_esik_yuzde`), ön uç sözleşmesinde de taşınır.

⊘ **KARAR: LMDI'ye GEÇİLMİYOR.** Geçmek, **tam toplanabilir** bir yöntemi sıfır/negatifte
**tanımsız** bir yöntemle değiştirmek olurdu — yani kartın kaçınmak istediği sorunu
**davet etmek**.
"""

from __future__ import annotations

from app.contribution import contributions, decompose

_SATIRLAR = [
    {"makine": "RAM-1", "fire": 120.0, "fire_gecen": 100.0},
    {"makine": "RAM-2", "fire": 80.0, "fire_gecen": 130.0},
    {"makine": "RAM-3", "fire": 0.0, "fire_gecen": 40.0},     # → SIFIR (ln tanımsız olurdu)
    {"makine": "RAM-4", "fire": -10.0, "fire_gecen": 5.0},    # → NEGATİF
    {"makine": "RAM-5", "fire": 50.0, "fire_gecen": 50.0},    # → değişim YOK
]


def test_PARCALARIN_TOPLAMI_BUTUNU_VERIR():
    """🔴 **Alt-grup toplanabilirliği** — kartın *«yok»* dediği özellik **var** ve tam."""
    k = contributions(_SATIRLAR, "makine", "fire")
    toplam_delta = sum(x["delta"] for x in k)
    butun = sum(r["fire"] for r in _SATIRLAR) - sum(r["fire_gecen"] for r in _SATIRLAR)
    assert abs(toplam_delta - butun) < 1e-9, (
        f"🔴 parçaların toplamı ({toplam_delta}) bütünün farkını ({butun}) vermiyor — "
        "toplamsal ayrıştırma bozulmuş.")


def test_SIFIR_BILESEN_COKMEZ():
    """⊘ `ln(0)` kaygısı konu dışı: sıfıra düşen bir segment normal işlenir."""
    k = {x["deger"]: x for x in contributions(_SATIRLAR, "makine", "fire")}
    assert k["RAM-3"]["delta"] == -40.0


def test_NEGATIF_BILESEN_COKMEZ():
    """⊘ Negatifte LMDI tanımsızdır; çıkarma **her işarette** tanımlıdır."""
    k = {x["deger"]: x for x in contributions(_SATIRLAR, "makine", "fire")}
    assert k["RAM-4"]["delta"] == -15.0


def test_SIRA_BAGIMSIZ():
    """⚠ Toplamsal ayrıştırma sıraya bağlı değildir — LMDI'nin çözdüğü ikinci sorun da
    burada **zaten yok**."""
    a = {x["deger"]: x["delta"] for x in contributions(_SATIRLAR, "makine", "fire")}
    b = {x["deger"]: x["delta"]
         for x in contributions(list(reversed(_SATIRLAR)), "makine", "fire")}
    assert a == b


def test_GOVDEDE_LOGARITMA_YOK():
    """🔴 Kartın öncülü *«LMDI-II ailesinde»* idi. Yüklem **yapısal**: ayrıştırma
    gövdesinde logaritma geçmiyor.

    ⚠ `math.log2` bu modülde **var** ama `§E2`'nin Jensen-Shannon sürprizinde — ayrı bir
    fonksiyon, ayrı bir iş. *Bir modülde bir sembolün bulunması, onu her fonksiyonun
    kullandığı anlamına gelmez.*
    """
    import inspect

    govde = inspect.getsource(contributions)
    for iz in ("log", "ln("):
        assert iz not in govde, (
            f"🔴 ayrıştırma gövdesinde `{iz}` geçiyor — yöntem artık toplamsal olmayabilir; "
            "`§E7` kararı (LMDI'ye geçilmiyor) yeniden okunmalı.")


def test_KIRPMA_SESSIZ_DEGIL():
    """⚠ Tek *«toplam %100 değil»* etkisi bir **sunum** kararıdır ve makbuzu olmalı:
    kaç segment kırpıldı **ve** hangi eşikle. *Sessiz kırpma «her şey kapsandı» gibi
    okunur.*"""
    r = decompose(_SATIRLAR, "makine", "fire", {"cube": "oee", "measures": ["fire"]})
    assert "kirpilan_segment" in r and "kirpilan_esik_yuzde" in r, (
        "🔴 kırpma beyanı eksik — kullanıcı eksik toplamı bir hata sanar.")
    assert r["kirpilan_esik_yuzde"] > 0
