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

    🔴 **İlk yazımım kırılgandı** (bir denetim ajanı ölçtü, 2026-08-12):
    `inspect.getsource()` **docstring'i ve yorumları da** döndürür. Yani gövdeye
    *«burada logaritma YOK»* diye bir yorum yazan biri bu kapıyı **yanlış-kırmızı**
    yapardı — ve bu, bu turda `test_d7`'de ölçülen kusurun **aynadaki hâlidir**: orada
    bir yorum kapıyı haksız **yeşil**, burada haksız **kırmızı** yapıyordu.

    ✅ Yüklem artık `ast` üstünde: bir docstring `ast.Constant`'tır, çağrılan bir
    logaritma `ast.Name`/`ast.Attribute`. *Bir davranışı ölçen yüklem, o davranışı
    anlatan metni kanıt saymamalıdır — hangi yöne çevirirse çevirsin.*
    """
    import ast
    import inspect
    import textwrap

    agac = ast.parse(textwrap.dedent(inspect.getsource(contributions)))
    adlar = {n.id for n in ast.walk(agac) if isinstance(n, ast.Name)}
    adlar |= {n.attr for n in ast.walk(agac) if isinstance(n, ast.Attribute)}
    kacak = {a for a in adlar if a in {"log", "log2", "log10", "ln", "logaddexp"}}
    assert not kacak, (
        f"🔴 ayrıştırma gövdesi bir logaritma ÇAĞIRIYOR: {kacak} — yöntem artık "
        "toplamsal olmayabilir; `§E7` kararı (LMDI'ye geçilmiyor) yeniden okunmalı.")
    assert adlar, "⊘ ölçüm tabanı çöktü: gövdeden hiç ad okunamadı"


def test_KIRPMA_SESSIZ_DEGIL():
    """⚠ Tek *«toplam %100 değil»* etkisi bir **sunum** kararıdır ve makbuzu olmalı:
    kaç segment kırpıldı **ve** hangi eşikle. *Sessiz kırpma «her şey kapsandı» gibi
    okunur.*"""
    # 🔴🔴 **YÜKLEM GÜÇLENDİRİLDİ** (⟳ 08-12, denetim bulgusu). Eski hâli yalnız
    # **anahtar varlığına** bakıyordu ve **hiç kırpma olmayan** veride de yeşildi —
    # yani *«kırpma sessiz değil»* iddiasının arkasında **tek bir bit** vardı.
    # ⚠ Artık GERÇEKTEN kırpan veriyle ölçülüyor ve **kütle** de isteniyor.
    r = decompose(_SATIRLAR, "makine", "fire", {"cube": "oee", "measures": ["fire"]})
    for alan in ("kirpilan_segment", "kirpilan_esik_yuzde", "kirpilan_pay_yuzde"):
        assert alan in r, f"🔴 kırpma beyanında `{alan}` yok — kullanıcı eksik toplamı bir hata sanar."
    assert r["kirpilan_esik_yuzde"] > 0

    # gerçekten kırpan veri: 1 büyük + 40 küçük segment
    satirlar = [{"makine": f"S{i}", "fire": v, "fire_gecen": 0.0}
                for i, v in enumerate([1000.0] + [1.0] * 40)]
    k = decompose(satirlar, "makine", "fire", {"cube": "oee", "measures": ["fire"]})
    assert k["kirpilan_segment"] > 0, (
        "⊘ ölçüm tabanı çöktü: bu veride kırpma ATEŞLEMEDİ — yüklem boşa düşüyor.")
    assert k["kirpilan_pay_yuzde"] > 0, (
        "🔴 kırpılan KÜTLE sıfır bildiriliyor — *«kaç segment» bir kapsam beyanı "
        "değildir; «ne kadarı» beyandır.*")
    gosterilen = sum(abs(b.get("brut_pay") or 0.0) for b in k["bulgular"])
    assert abs(gosterilen + k["kirpilan_pay_yuzde"] - 100.0) < 1.0, (
        f"🔴 BEYAN KAPANMIYOR: gösterilen %{gosterilen:.1f} + kırpılan "
        f"%{k['kirpilan_pay_yuzde']:.1f} ≠ %100 — bir kısmı **adsız** kalıyor.")


def test_ON_UC_ESIGI_IKI_KEZ_YUZDEYE_CEVIRMIYOR():
    """🔴 **BİRİM HATASI** — ekranda *«|pay| < %100.0»* yazıyordu (⟳ 08-12).

    Backend `_GURULTU_PAYI = 1.0` gönderiyor ve bu **zaten yüzde**
    (`abs(delta)/brut*100 >= 1.0`). Ön uç bir kez daha `*100` uyguluyordu:

        {(r.kirpilan_esik_yuzde * 100).toFixed(1)}   →  %100.0

    Yani beyan, **her şeyin** kırpıldığını söylüyordu — *bir birim hatası, beyanı
    kendi tersine çevirir.* Ayrıca PVM dalı eşiği **hiç** yazmıyordu; o da eklendi.
    """
    import pathlib as _p

    fe = (_p.Path(__file__).parent.parent.parent / "dima-frontend-demo-master"
          / "src" / "components" / "ContributionLayer.tsx")
    if not fe.is_file():
        import pytest
        pytest.skip("⊘ ön uç bağlanmamış — `-v \"$PWD/dima-frontend-demo-master:…:ro\"`")
    m = fe.read_text(encoding="utf-8")
    assert "kirpilan_esik_yuzde * 100" not in m, (
        "🔴 ön uç eşiği İKİ KEZ yüzdeye çeviriyor → ekranda «%100.0». Backend zaten "
        "yüzde gönderiyor.")
    assert m.count("kirpilan_esik_yuzde.toFixed(1)") >= 2, (
        "🔴 iki kırpma beyanından biri eşiği YAZMIYOR — *«kaç segment» tek başına "
        "«hangi eşikle» sorusunu cevaplamaz.*")
