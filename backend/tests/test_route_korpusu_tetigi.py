"""🔴 `A7` — **ROUTE KORPUSU DEĞİŞİKLİK-TETİKLİDİR.**

Raporun `§4i` kararı: kapının merkezi kasetli garson korpusudur (her demet, sıfır API);
route korpusu (~10.800 soru, **13–20 dk CPU**) *"her demet"* değil **kritik
değişiklikte + günde 1** koşar.

⊙ Gerekçe ölçülmüş: route korpusu iki eksen görür — **payda** (*kaç soru
cevaplanabiliyor*) ve **`sessiz_yanlis`**. İkisi de ancak **route'un kendisi ya da
katalog** değiştiğinde kıpırdar. Bir anlatı düzeltmesinden sonra 13 dakika beklemek,
*ölçmediğini ölçmek için* ödenen bir bedeldir.
"""

from __future__ import annotations

import pytest

from lab.kapi import route_korpusu_gerekli


@pytest.mark.parametrize("degisen", [
    ["app/cube_router.py"],
    ["app/wren_service.py"],
    ["backend/demo/packs/boyahane/cubes/parti/metadata.yml"],
    ["app/answer.py", "app/katalog_metni.py"],          # biri yeterli
])
def test_TETIKLEYICIYE_DOKUNULDUYSA_KOSAR(degisen):
    gerekli, gerekce = route_korpusu_gerekli(degisen)
    assert gerekli, gerekce
    assert "tetikleyici" in gerekce


@pytest.mark.parametrize("degisen", [
    ["app/answer.py"],
    ["app/diyalog.py", "tests/test_odak_varlik.py"],
    ["belgeler/KAPI-DEFTERI.md"],
])
def test_DOKUNULMADIYSA_ATLANIR(degisen):
    gerekli, _ = route_korpusu_gerekli(degisen)
    assert not gerekli


def test_LISTE_YOKSA_KOSAR():
    """🔴 Bilinmeyen bir değişiklik **en kötüsü** sayılır.

    *Ölçmediğini güvenli saymak, bu deponun üç kez ödediği hatadır* — ve bir tetikleyici
    varsayılan olarak *atla* deseydi, listeyi vermeyi unutmak kapıyı sessizce kapatırdı.
    """
    assert route_korpusu_gerekli([])[0] is True


def test_TETIK_LISTESI_ELLE_DEGIL_DESENLE():
    """⚠ Elle tutulan bir tetik listesi, bir gün eklenen dosyayı görmez.

    `demo/packs/` bir **önek**tir: yarın eklenen bir pack kendiliğinden kapsanır.
    """
    from lab.kapi import ROUTE_TETIKLEYICILERI

    assert any(t.endswith("/") for t in ROUTE_TETIKLEYICILERI), \
        "en az bir tetikleyici DİZİN öneki olmalı — yoksa yeni dosyalar kapsanmaz"
    assert route_korpusu_gerekli(["demo/packs/YENI_SEKTOR/cubes/x/metadata.yml"])[0]
