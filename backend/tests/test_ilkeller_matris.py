"""FAZ 7b — KARAR MATRİSİ. *Bir karşılaştırma tablosu, bir karar değil.*

## Neden bu kapı `MIMARI §12.9`'la çelişmiyor

O bölüm *"seçenekler × ölçütler × ağırlıklar"* matrisini **bilinçle reddediyor**:
*«kontrol edilebilirlik · uygulama maliyeti · risk … hiçbiri veride yok ve tahmin
edilemez … `source=cube` rozetiyle uydurma sıralama»*.

| reddedilen | buradaki |
|---|---|
| ölçütler **uydurulur** | ölçütler **katalogda var olan ölçüler** |
| ağırlıklar modelden | 🔴 **ağırlık YOK** |
| sıralama bir **yargı** | sıralama bir **ölçüm** |
"""

from __future__ import annotations

from app.ilkeller import matris, sirala

A = [{"m": "X", "ciro": 100}, {"m": "Y", "ciro": 200}, {"m": "Z", "ciro": 150}]
B = [{"m": "X", "fire": 10}, {"m": "Y", "fire": 40}]          # ⚠ Z YOK — eksik hücre


def test_MATRIS_ADAYLARI_HIZALAR():
    r = {x["m"]: x for x in matris([A, B], "m")}
    assert r["X"] == {"m": "X", "ciro": 100, "fire": 10}
    assert set(r) == {"X", "Y", "Z"}, "bir adayda eksik ölçüt varsa aday DÜŞMEZ"


def test_EKSIK_HUCRE_SIFIR_YAZILMAZ():
    """🔴 Bir adayda o ölçü hiç yoksa *«sıfır»* demek, yokluğu bir değere çevirmektir."""
    r = {x["m"]: x for x in matris([A, B], "m")}
    assert "fire" not in r["Z"], f"eksik hücre uydurulmuş: {r['Z']}"


def test_YON_BEYANDAN_OKUNUR():
    """🔴 `§W-C` — *az olan iyi* mi, sözlükten değil **`lower_is_better` beyanından**."""
    m = matris([A, B], "m")
    yuksek = sirala(m, "m", ["ciro"])[0]["m"]
    dusuk = sirala(m, "m", ["ciro"], az_iyi={"ciro"})[0]["m"]
    assert (yuksek, dusuk) == ("Y", "X"), "yön beyanı sıralamayı çevirmedi"


def test_AGIRLIK_ALANI_YOK_VE_OLMAYACAK():
    """🔴🔴 *«Sayıyı her zaman küp koyar»* ilkesinin karar-matrisi karşılığı.

    Bir `agirliklar` alanı açmak yasakladığımız aritmetiği **arka kapıdan** geri
    getirirdi: model bir sayı uydurur, o sayı sıralamayı belirler ve sonuç
    `source=cube` rozetiyle döner.
    """
    import inspect

    from app.plan_semasi import ZORUNLU_ALANLAR, plan_json_schema
    assert "agirlik" not in str(ZORUNLU_ALANLAR).lower()
    _sema = plan_json_schema({"oee": {"measures": ["ciro"], "dimensions": ["m"]}})
    assert "agirlik" not in str(_sema).lower(), "şemaya ağırlık alanı sızmış"
    assert "agirlik" not in inspect.signature(sirala).parameters


def test_EKSIK_OLCUT_CEZA_DEGIL_VE_PAYDA_YAZILIR():
    """⚠ Eksik veriyle en kötü sıraya düşürmek, **ölçülmemiş** olanı ölçülmüş gibi
    cezalandırmaktır. Ve kaç ölçütle sıralandığı **görünmeden** sıra okunamaz."""
    r = {x["m"]: x for x in sirala(matris([A, B], "m"), "m", ["ciro", "fire"])}
    assert r["Z"]["_olcut_sayisi"] == 1 and r["X"]["_olcut_sayisi"] == 2
    assert r["Z"]["_skor"] is not None, "eksik ölçüt adayı skorsuz bıraktı"


def test_SKORSUZ_ADAY_SILINMEZ_SONA_KONUR():
    """⚠ Bir adayı listeden düşürmek, onu **değerlendirilmiş** göstermektir."""
    out = sirala([{"m": "X", "ciro": 5}, {"m": "Q"}], "m", ["ciro"])
    assert [x["m"] for x in out] == ["X", "Q"]
    assert out[-1]["_skor"] is None and out[-1]["_olcut_sayisi"] == 0


def test_TEK_SATIRDA_BOLME_YOK():
    """⚠ Min=maks olduğunda normalleştirme sıfıra bölerdi."""
    assert sirala([{"m": "X", "ciro": 7}], "m", ["ciro"])[0]["_skor"] == 1.0
