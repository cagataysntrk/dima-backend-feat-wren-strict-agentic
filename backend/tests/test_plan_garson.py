"""FAZ O-4 — PLANLAYICI İLE GARSON **AYNI KİŞİ**.

Kullanıcının sorusu şuydu: *"planlayıcı ile llm intent yani garson aynı kişi olabilir…
çünkü llm'e iki istek yerine tek cevapta bunu halledebiliriz."* Bu kapı o denkliğin
kurulduğunu ve **bedelinin ödenmediğini** ölçer: çağrı sayısı artmıyor.
"""

from __future__ import annotations

import json

from app.plan_garson import PlanGarsonu, sarmala

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


def _g(yanit):
    ic = _Sahte(yanit)
    return PlanGarsonu(ic, {"oee": {"measures": ["ort_oee"], "dimensions": ["makine"]}}), ic


def test_TEK_ADIMLI_PLAN_BUGUNKU_CEVAPLA_DENK():
    """🔴🔴 `E6`'nın yarısı burada siliniyor — basit soruda çıktı **bire bir** aynı."""
    g, ic = _g(json.dumps({"adimlar": [{"fiil": "SORGU", "cube_query": CQ}]}))
    assert json.loads(g.select_cube("q", "kat")) == CQ
    assert g.planlar == [], "tek adımlı plan saklanmamalı — o zaten CubeQuery olarak döndü"


def test_LLM_TURU_ARTMIYOR():
    """🔴 Planlayıcı `select_cube`'un **YERİNE** geçer, yanına değil.

    *Bir yeteneği eklemenin en sessiz bedeli, her soruya bir çağrı daha eklemektir —
    ve o bedel ancak sayılırsa görünür.*
    """
    g, ic = _g(json.dumps({"adimlar": [{"fiil": "SORGU", "cube_query": CQ}]}))
    g.select_cube("q", "kat")
    assert (ic.sayac["plan"], ic.sayac["cube"]) == (1, 0), (
        f"tek soru için {sum(ic.sayac.values())} çağrı yapıldı: {ic.sayac}")


def test_COK_ADIMLI_PLAN_BUGUNKU_CEVABI_YOK_ETMEZ():
    """🔴🔴 `E3` — ve bu kapı **ölçümden** doğdu, tasarımdan değil.

    İlk hâl burada `"{}"` döndürüyordu (*«çok adımlı bir soru zaten tek cube ile
    cevaplanamaz»*). `EE` turunun A/B'si çürüttü: `EE6` *«geçen hafta hiç iş kazası oldu
    mu»* bayrak kapalıyken `isg`/`{kaza_adedi: 0}` veriyor, açıkken **cevapsız** kalıyordu.

    ⊙ Orkestratör merdivenin **boşluğuna** girmeliydi; **yerine** geçmişti.
    """
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "BAGLA", "kaynak": "$1", "boyut": "makine",
                         "olcu": "ort_oee"}]}
    g, ic = _g(json.dumps(plan))
    assert json.loads(g.select_cube("q", "kat")) == CQ, (
        "çok adımlı plan BUGÜNKÜ cevabı yok etti — E3 ihlali")
    assert ic.sayac["cube"] == 1, "bugünkü yol AYRICA sorulmalıydı"
    assert g.cok_adimli_plan() == plan, "plan saklanmadı — boşluk dolduralamaz"


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
        g, ic = _g(json.dumps({"adimlar": [kotu]}))
        assert json.loads(g.select_cube("q", "kat")) == CQ, f"{kotu} plan sayıldı"
        assert ic.sayac["cube"] == 1


def test_BILINMEYEN_FIIL_PLANI_HIC_DOGMAZ():
    """⚠ Beyaz liste çalıştırıcıdan **önce**: ilk adım koşmadan reddedilir."""
    g, ic = _g(json.dumps({"adimlar": [{"fiil": "SQL_YAZ", "kaynak": "$1"}]}))
    assert json.loads(g.select_cube("q", "kat")) == CQ, "bugünkü yola inilmeliydi"
    assert ic.sayac["cube"] == 1


def test_PLAN_YOLU_DUSERSE_BUGUNKU_YOL_KALIR():
    """🔴 Fail-open: bir genişleme, genişlettiği şeyi **bozamaz**."""
    class _Patlak(_Sahte):
        def plan_kur(self, question, catalog, sema=None):
            raise RuntimeError("sağlayıcı düştü")

    ic = _Patlak("")
    g = PlanGarsonu(ic, {})
    assert json.loads(g.select_cube("q", "kat")) == CQ
    assert ic.sayac["cube"] == 1


def test_BAYRAK_KAPALIYKEN_SARMALANMAZ():
    """🔴🔴 `KURAL B` — kapalıyken **nesnenin kendisi** döner, bir sarmalayıcı bile değil.

    *Bir kill-switch'in kanıtı «aynı davranış» değil, «aynı nesne»dir.*
    """
    ic = _Sahte("{}")
    assert sarmala(ic, {}, None, None) is ic


def test_SAYDAM_SARMALAYICI():
    """⚠ Sarmalayıcı, sarmaladığı yüzeyi **daraltmaz**."""
    ic = _Sahte("{}")
    ic.refine_cube = lambda *a: "x"
    g = PlanGarsonu(ic, {})
    assert g.refine_cube("a", "b", "c") == "x"
    assert g.sema_kullanir is False
