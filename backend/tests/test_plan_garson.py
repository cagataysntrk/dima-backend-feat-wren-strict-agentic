"""FAZ O-4 — PLANLAYICI İLE GARSON **AYNI KİŞİ**.

Kullanıcının sorusu şuydu: *"planlayıcı ile llm intent yani garson aynı kişi olabilir…
çünkü llm'e iki istek yerine tek cevapta bunu halledebiliriz."* Bu kapı o denkliğin
kurulduğunu ve **bedelinin ödenmediğini** ölçer: çağrı sayısı artmıyor.
"""

from __future__ import annotations

import json

from app.plan_garson import acik_mi, plan_uret

CQ = {"cube": "oee", "measures": ["ort_oee"]}


class _Sahte:
    """Bugünkü sağlayıcı sözleşmesi. `sayac` iki yolu AYRI sayar."""

    sema_kullanir = False
    plan_kurabilir = True

    def __init__(self, plan_yaniti: str):
        self._y, self.sayac = plan_yaniti, {"plan": 0, "cube": 0}

    def plan_kur(self, question, catalog, sema=None):
        self.sayac["plan"] += 1
        return self._y

    def select_cube(self, question, catalog, sema=None):
        self.sayac["cube"] += 1
        return json.dumps(CQ)


IDX = {"oee": {"measures": ["ort_oee"], "dimensions": ["makine"]}}


def _g(yanit):
    ic = _Sahte(yanit)
    return ic, (lambda: plan_uret(ic, "q", "kat", IDX))


def test_PLAN_SELECT_CUBE_ILE_YARISMAZ():
    """🔴🔴 **ÖLÇÜMÜN ZORUNLU KILDIĞI YERLEŞİM.** Plan `select_cube`'un yerine geçtiğinde
    `EE` turunun A/B'si arıza oranını **%55 → %65** ölçtü (+10 puan).

    ⊙ Mekanizma: `_select_consistent` `k` örneği **aynı** süreçten çeker ve oylar. Plan
    araya girince örneklerin bir kısmı plandan, bir kısmı `select_cube` yedeğinden
    geliyordu. *Bir oylamanın geçerliliği örneklerin özdeşliğine dayanır.*

    Bu kapı yerleşimi kilitler: plan üretimi `select_cube`'u **hiç çağırmaz**.
    """
    ic, uret = _g(json.dumps({"adimlar": [{"fiil": "SORGU", "cube_query": CQ}]}))
    uret()
    assert ic.sayac["cube"] == 0, (
        "plan üretimi `select_cube`'a dokundu — oylama iki farklı süreçten beslenir")


def test_BAYRAK_KAPALIYKEN_HIC_KOSMAZ():
    """🔴🔴 `KURAL B` — kapalıyken bu modülün hiçbir satırı koşmaz."""
    assert acik_mi(None, None, _Sahte("{}")) is False


def test_SAGLAYICI_PLAN_KURAMIYORSA_ACILMAZ():
    """⚠ Yetenek **sorulur**, tahmin edilmez — ve varsayılan `False` (fail-closed)."""
    class _Yeteneksiz:
        plan_kurabilir = False
    assert acik_mi(None, None, _Yeteneksiz()) is False
    assert acik_mi(None, None, object()) is False


def test_SOZLESMESI_EKSIK_ADIM_PLAN_SAYILMAZ():
    """🔴 **ADI DOĞRU, SÖZLEŞMESİ YANLIŞ.** Ölçüldü (`EE`, canlı serbest-JSON):

        {"fiil":"SORGU"}                          ← `cube_query` YOK
        {"fiil":"AYRISTIR","ozellik":…,"detay":…} ← uydurma alanlar

    Yalnız fiil adına bakan doğrulama bunları plan sanıyordu; çalıştırıcı `KeyError` ile
    düşüyor ve **cevaplanabilir** bir soru cevapsız kalıyordu.
    """
    for kotu in ({"fiil": "SORGU"},
                 {"fiil": "AYRISTIR", "ozellik": "maliyet", "detay": "x"},
                 {"fiil": "BAGLA", "kaynak": "$1"}):
        _, uret = _g(json.dumps({"adimlar": [kotu]}))
        assert uret() is None, f"{kotu} plan sayıldı"


def test_GECERLI_PLAN_URETILIYOR():
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "BAGLA", "kaynak": "$1", "boyut": "makine",
                         "olcu": "ort_oee"}]}
    _, uret = _g(json.dumps(plan))
    assert uret() == plan


def test_BILINMEYEN_FIIL_PLANI_HIC_DOGMAZ():
    """⚠ Beyaz liste çalıştırıcıdan **önce**: ilk adım koşmadan reddedilir."""
    _, uret = _g(json.dumps({"adimlar": [{"fiil": "SQL_YAZ", "kaynak": "$1"}]}))
    assert uret() is None


def test_PLAN_YOLU_DUSERSE_TUR_DUSMEZ():
    """🔴 Fail-open: bir genişleme, genişlettiği şeyi **bozamaz**."""
    class _Patlak(_Sahte):
        def plan_kur(self, question, catalog, sema=None):
            raise RuntimeError("sağlayıcı düştü")
    assert plan_uret(_Patlak(""), "q", "kat", IDX) is None
