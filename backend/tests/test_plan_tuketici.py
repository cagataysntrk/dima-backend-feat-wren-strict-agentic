"""FAZ O-4 tüketici — BOŞLUĞU DOLDURUYOR MU, ve DOLDURAMAYINCA NE SÖYLÜYOR.

Raporun `O-4` başarı ölçütü **iki dallı**: *«cevap üretiyor **ya da** neden üretemediğini
adım adım söylüyor»*. İkinci dal bir kaçış değil bir üründür — bugünkü karşılığı tek
cümlelik bir rettir ve kullanıcı ondan hiçbir şey öğrenemez.
"""

from __future__ import annotations

import json

import pytest

from app import plan_tuketici as pt
from app.plan_kosucu import PlanHatasi

ROWS = [{"makine": "RAM-1", "ort_oee": 0.58}, {"makine": "RAM-2", "ort_oee": 0.60},
        {"makine": "RAM-3", "ort_oee": 0.5245}, {"makine": "X", "ort_oee": 0.59}]
CQ = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}
PLAN = {"adimlar": [
    {"fiil": "SORGU", "cube_query": CQ},
    {"fiil": "BAGLA", "kaynak": "$1", "boyut": "makine", "olcu": "ort_oee"},
    {"fiil": "HESAPLA", "kaynak": "$1", "hedef": "$2", "boyut": "makine",
     "olcu": "ort_oee"}]}
SCHEMA = {"cubes": [{"name": "oee", "measures": ["ort_oee"],
                     "dimensions": ["makine"], "lower_is_better": []}]}


class _Motor:
    def cube_sql(self, cq): return "SELECT 1"
    def dry_plan(self, sql): return {}
    def query(self, sql, limit=None):
        return {"columns": ["makine", "ort_oee"], "rows": ROWS, "row_count": len(ROWS)}


class _Garson:
    """Sağlayıcı taklidi: `plan_kur` bir plan METNİ döndürür (gerçek sözleşme)."""

    sema_kullanir = False
    plan_kurabilir = True

    def __init__(self, plan): self._p = plan

    def plan_kur(self, question, catalog, sema=None):
        return json.dumps(self._p) if self._p else "{}"


@pytest.fixture(autouse=True)
def _bayrak_acik(monkeypatch):
    """⚠ Bayrak testte AÇIK tutulur — kapalı hâlin kendi kapısı ayrı (`test_BAYRAK…`)."""
    from app import plan_garson
    monkeypatch.setattr(plan_garson, "acik_mi", lambda *a, **k: True)


class _Istek:
    """`request.app.state.llm` — üretimdeki tek gerçek kaynak."""

    def __init__(self, llm):
        self.app = type("A", (), {"state": type("S", (), {"llm": llm})()})()


def _cevap(g, motor=None, soru="q"):
    return pt.cevap(_Istek(g), service=motor or _Motor(), schema=SCHEMA, soru=soru)


def test_BAYRAK_KAPALIYKEN_HIC_KONUSMAZ(monkeypatch):
    """🔴🔴 `KURAL B` — bayrak kapalıyken dal **hiç açılmaz**."""
    from app import plan_garson
    monkeypatch.setattr(plan_garson, "acik_mi", lambda *a, **k: False)
    assert _cevap(_Garson(PLAN)) is None


def test_PLAN_CIKMAZSA_MERDIVEN_BUGUNKU_GIBI():
    assert _cevap(_Garson(None)) is None


def test_SAGLAYICI_YOKSA_PATLAMAZ():
    """🔴 Ölçüldü (`EE19`, canlı): sağlayıcı çağıranın **yerelinden** okunuyordu ve
    deterministik yoldan gelindiğinde `UnboundLocalError` — bayrak KAPALIYKEN de.

    *Koşullu bağlanan bir ad, tanımsız bir addan daha sinsidir: statik olarak var,
    çalışırken yok.*
    """
    assert pt.cevap(_Istek(None), service=_Motor(), schema=SCHEMA, soru="q") is None
    assert pt.cevap(object(), service=_Motor(), schema=SCHEMA, soru="q") is None


def test_BOSLUKTA_CEVAP_URETIYOR():
    """🔴 Üç adım koştu, tek sorgu, ve cevabın içinde **bulgu** var — makbuz değil sonuç."""
    c = _cevap(_Garson(PLAN))
    assert c["source"] == "cube+llm"
    assert "3 adımda üretildi" in c["note"]
    assert "RAM-3" in c["note"], "BAGLA'nın seçtiği varlık cevaba girmedi"
    assert "%11.1" in c["note"], "HESAPLA'nın farkı cevaba girmedi"
    assert c["result"]["row_count"] == 4
    assert c["cube_query"] == CQ, "makbuz TIKLANABİLİR olmalı (O-5: /cube ile 0 LLM)"


def test_HAM_FLOAT_SIZMAZ():
    """⚠ `§AA1`'in dersi: `0.5245118291704627` bir cevap değil, bir sızıntıdır."""
    c = _cevap(_Garson(PLAN))
    assert "0.5245118" not in c["note"]


def test_KOSAMAYINCA_ADIM_ADIM_SOYLUYOR():
    """🔴🔴 `O-4`'ün İKİNCİ başarı ölçütü — *«neden üretemediğini adım adım söylüyor»*.

    Bugünkü karşılığı: *«Bu soru için güvenilir bir sorgu üretemedim.»*
    """
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "TREND", "kaynak": "$1"}]}
    c = _cevap(_Garson(plan))
    assert c["source"] is None, "koşamayan bir plan CEVAP VERMİŞ gibi görünemez"
    assert "1." in c["note"] and "2." in c["note"], "adımlar sayılmamış"
    assert "TREND" in c["note"] and "tamamlayamadım" in c["note"]


def test_KATALOG_DISI_SORGU_MOTORA_GITMEZ():
    """🔴 Beyaz liste planın İÇİNDE de geçerli — bir adım Discovery'ye dönüşemez."""
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": {"cube": "uydurma"}}]}
    with pytest.raises(PlanHatasi, match="katalogda karşılanmıyor"):
        pt.calistir(plan, service=_Motor(), index={"oee": {"measures": ["ort_oee"]}})


def test_BEKLENMEYEN_ARIZA_MERDIVENI_BOZMAZ():
    """⚠ Fail-open: tüketici düşerse `None` döner ve bugünkü yol aynen sürer."""
    class _Patlak(_Motor):
        def query(self, sql, limit=None): raise RuntimeError("motor düştü")
    assert _cevap(_Garson(PLAN), _Patlak()) is None
