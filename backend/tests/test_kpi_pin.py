"""FAZ 5.10 kapısı — **KPI pin semantiği.** [bayrak: `kpi_pin`]

Yol haritasının üç şartı:

1. Pin edilen KPI `dashboards`'ın **10/kullanıcı** sınırına tabi — **yeni sınır icat
   EDİLMEZ**.
2. NL yolu (*"bunu panoya sabitle"*) 5.1'in sınıflandırmasından geçer — **ikinci bir
   niyet çözücü yazılmaz**.
3. `kpi_pin=off` → pano bugünkü davranışta; **panel sayısı ARTMAZ** (K5 · PK-1).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app import kpi_pin


def _w(i, pinned=False):
    return {"id": f"w{i}", "title": f"W{i}", "pinned": pinned}


def test_1_YENI_SINIR_ICAT_EDILMEZ():
    """🔴 İkinci bir tavan, **aynı kuralın iki sahibi** olurdu ve ikisi ayrışırdı.

    ⚠ Belirteç **AST**: `kpi_pin.py`'de sayısal bir tavan sabiti **olmamalı** — sınır
    `dashboards`'ın kendi sabitinden okunur.
    """
    from app.routers.dashboards import _MAX_PER_USER

    assert kpi_pin.azami_pin() == _MAX_PER_USER

    # ⚠ Belirteç **MODÜL DÜZEYİ + SAYISAL SABİT**e daraltıldı — ilk yazımda `ast.walk`
    # gövde içindeki `tavan = ...` **yerel değişkenini** yakalayıp yanlış-pozitif verdi.
    # O satır tam da doğru davranışın kendisiydi: sınırı `dashboards`'tan **okuyordu**.
    # *Bir kuralı ölçen belirteç, kuralın uygulandığı hâli cezalandırmamalı.*
    agac = ast.parse((Path(__file__).resolve().parents[1] / "app/kpi_pin.py")
                     .read_text(encoding="utf-8"))
    for n in agac.body:                                   # yalnız modül düzeyi
        if not isinstance(n, (ast.Assign, ast.AnnAssign)):
            continue
        hedefler = n.targets if isinstance(n, ast.Assign) else [n.target]
        deger = n.value
        if not (isinstance(deger, ast.Constant) and isinstance(deger.value, int)):
            continue
        for h in hedefler:
            ad = getattr(h, "id", "")
            assert not any(k in ad.upper() for k in ("MAX", "AZAMI", "TAVAN", "SINIR")), (
                f"🔴 `kpi_pin.py` KENDİ sayısal tavanını tanımlamış: {ad}. Kopyalanmış "
                f"bir sabit, bir gün ötekinden ayrışır.")


def test_2_IKINCI_NIYET_COZUCU_yok():
    """*"Bunu panoya sabitle"* zaten `eylem.tespit()`'in `_PANO_KALIP` ailesinde."""
    from app import eylem
    from app.cube_router import _norm

    assert eylem.tespit(_norm("bunu panoya ekle")) == eylem.PANO_EKLE
    # `kpi_pin.py` kendi kalıp sözlüğü KURMAMALI.
    kaynak = (Path(__file__).resolve().parents[1] / "app/kpi_pin.py").read_text(
        encoding="utf-8")
    agac = ast.parse(kaynak)
    for n in ast.walk(agac):
        if isinstance(n, ast.Assign):
            for h in n.targets:
                if getattr(h, "id", "").startswith("_KALIP") or \
                   getattr(h, "id", "") in ("_PANO_KALIP", "_PIN_KALIP"):
                    raise AssertionError(
                        "🔴 İkinci bir niyet çözücü doğmuş — niyet tanıma TEK yerde kalır.")


def test_3_PIN_bir_KATMAN_panel_DEGIL():
    """🔴 Panel tavanı 13/13 dolu; pin var olan widget'ın bir **işaretidir**.

    Ayrı bir tablo, aynı nesnenin iki kaydı demekti ve silme/geri alma iki yerde
    yürütülürdü.
    """
    assert kpi_pin.PIN_ALANI == "pinned"
    from control_plane.models import DashboardWidget

    # Ayrı bir `KpiPin` tablosu YOK.
    import control_plane.models as m

    assert not hasattr(m, "KpiPin"), (
        "🔴 Ayrı bir pin tablosu doğmuş — pin bir KATMAN, bir depo değil.")
    assert "id" in DashboardWidget.model_fields


def test_SINIR_dolunca_SESSIZCE_eski_DUSURULMEZ():
    """🔴 *En eskiyi düşürmek "akıllı" değil, **sinsidir**.*

    Bir pin bir **karardır**; kullanıcının kendi eliyle koyduğu bir şeyi haber vermeden
    kaldırmak, ürünün onun yerine karar vermesidir.
    """
    dolu = [_w(i, pinned=True) for i in range(10)]
    k = kpi_pin.pin_karari(dolu, "yeni", azami=10)
    assert k["izin"] is False
    assert "önce birini kaldır" in k["sebep"]
    assert k["pinli_sayi"] == 10


def test_ZATEN_PINLI_widget_tekrar_saymaz():
    dolu = [_w(i, pinned=True) for i in range(10)]
    k = kpi_pin.pin_karari(dolu, "w3", azami=10)
    assert k["izin"] is True and k["sebep"] == "zaten pinli"


def test_SIRALAMA_kararli():
    """⚠ Pin bir **öncelik** işaretidir, bir yeniden düzenleme aracı değil."""
    ws = [_w(1), _w(2, pinned=True), _w(3), _w(4, pinned=True)]
    s = kpi_pin.sirala(ws)
    assert [w["id"] for w in s] == ["w2", "w4", "w1", "w3"]
    assert kpi_pin.sirala(s) == s, "sıralama idempotent değil"


def test_ESKI_widget_PINSIZ_dogar():
    """Alan yoksa `False` — *hiç kimse onları pin'lemedi* ve bu doğrudur."""
    assert kpi_pin.pinli_mi({"id": "x"}) is False
    assert kpi_pin.pinli_mi({}) is False


@pytest.mark.parametrize("n", [0, 1, 9])
def test_sinir_altinda_izin_var(n):
    assert kpi_pin.pin_karari([_w(i, pinned=True) for i in range(n)],
                              "yeni", azami=10)["izin"] is True
