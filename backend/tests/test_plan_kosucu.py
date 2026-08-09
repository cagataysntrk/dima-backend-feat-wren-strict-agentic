"""FAZ O-2 — PLAN ÇALIŞTIRICISININ KAPISI.

Bu kapı **zincirin kurulabildiğini** kanıtlar: `SORGU → BAGLA → HESAPLA` bir soruyu
üç adımda cevaplıyor ve her adım bir öncekinin çıktısını **girdi olarak** alıyor.

⊙ Raporun `B3` boşluğu tam buydu: mutfak her adımı yapabiliyordu ama bir adımın çıktısını
ötekinin girdisine çeviren bir şey yoktu. Bu kapı o halkanın **kurulduğunu** ölçer.
"""

from __future__ import annotations

import pytest

from app.plan_kosucu import PlanHatasi, kos

ROWS = [{"m": "RAM-1", "v": 0.58}, {"m": "RAM-2", "v": 0.60},
        {"m": "RAM-3", "v": 0.5245}, {"m": "X", "v": 0.59}]


def _kos(plan, **kw):
    return kos(plan, sorgu_kos=lambda cq: ROWS, **kw)


def test_ZINCIR_KURULUYOR():
    """🔴🔴 `B3`'ün kapısı — bir adımın **çıktısı** ötekinin **girdisi** oluyor."""
    r = _kos({"adimlar": [
        {"fiil": "SORGU", "cube_query": {"cube": "oee", "measures": ["v"]}},
        {"fiil": "BAGLA", "kaynak": "$1", "boyut": "m", "olcu": "v"},
        {"fiil": "HESAPLA", "kaynak": "$1", "hedef": "$2", "boyut": "m", "olcu": "v"}]})
    assert r["ciktilar"][1] == ("RAM-3", 0.5245), "BAGLA hedefi seçemedi"
    h = r["ciktilar"][2]
    assert h["fark_yuzde"] == -11.1 and h["akran_sayisi"] == 3
    assert r["sorgu_sayisi"] == 1, "üç adımlık plan tek sorgu koşmalı"


def test_ILERI_REFERANS_TURU_DUSURUR():
    """⚠ `$3` üçüncü adımdayken **henüz yoktur**. Şema sıra bilmez; kapı burada."""
    with pytest.raises(PlanHatasi, match=r"\$3"):
        _kos({"adimlar": [{"fiil": "BAGLA", "kaynak": "$3", "boyut": "m", "olcu": "v"}]})


def test_BAGLANMAMIS_FIIL_SESSIZCE_ATLANMAZ():
    """🔴 Şemada olup çalıştırıcıda olmayan bir fiil **turu düşürür**.

    *Bir fiili şemaya koyup çalıştırıcıda unutmak, onu sessizce yalan yapmaktır.*
    """
    with pytest.raises(PlanHatasi, match="O-4"):
        _kos({"adimlar": [{"fiil": "ANLAT", "kaynak": "$1"}]})


def test_SORGU_BUTCESI_ASILAMAZ():
    """⚠ Bütçe aşımında **kısmi cevap yok**: hangi adımın eksik olduğunu kullanıcı aramaz."""
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": {"cube": "oee"}}] * 3}
    with pytest.raises(PlanHatasi, match="bütçe"):
        _kos(plan, azami_sorgu=2)


def test_BOS_PLAN_REDDEDILIR():
    with pytest.raises(PlanHatasi, match="boş"):
        _kos({"adimlar": []})


def test_YON_BEYANDAN_OKUNUR():
    """🔴 `§W-C`: *az olan iyi* mi — sözlükten değil **`lower_is_better` beyanından**.

    Aynı satırlarda aynı plan, beyan değişince **başka bir hedef** seçmeli.
    """
    plan = {"adimlar": [
        {"fiil": "SORGU", "cube_query": {"cube": "oee"}},
        {"fiil": "BAGLA", "kaynak": "$1", "boyut": "m", "olcu": "v"}]}
    assert _kos(plan)["ciktilar"][1][0] == "RAM-3"          # yüksek iyi → en düşüğü seç
    assert _kos(plan, cube_meta={"lower_is_better": ["v"]}
                )["ciktilar"][1][0] == "RAM-2"              # az iyi → en yükseği seç
