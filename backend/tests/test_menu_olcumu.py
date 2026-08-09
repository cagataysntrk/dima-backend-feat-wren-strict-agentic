"""FAZ O-8 — MENÜ ÖLÇÜM ALETİNİN KENDİ SINAVI (`G1`).

Raporun kabul ölçütü: *«rapor `Y6·AA13·X8·Z12`'yi **kendiliğinden** listeliyor»*.
Bu kapı onu ölçer — ve ölçerken raporun **kendi beklentilerinden ikisinin durum
değiştirdiğini** de kayda geçirir. *Bir kabul ölçütünü karşılamak, onu ezberlemek değil;
ölçtüğü şeyin bugünkü hâlini söyleyebilmektir.*
"""

from __future__ import annotations

import pytest

from lab import menu

SEMA = {"cubes": [
    {"name": "bakim", "measures": ["ort_durus_dakika"], "dimensions": ["makine"],
     "synonyms": ["bakım"]},
    {"name": "kalite", "measures": ["toplam_ek_sure_dk"], "dimensions": [],
     "measure_synonyms": {"toplam_ek_sure_dk": ["tamir süresi"]}},
    {"name": "sikayet", "measures": ["adet"], "dimensions": ["bolge"]},
]}


@pytest.fixture()
def _cevapli(monkeypatch):
    """⚠ `route()` sahteleniyor, `incele()` DEĞİL. Ölçülen şey aletin **kararı**:
    verilen bir cevabı beklenen konuyla karşılaştırabiliyor mu. Gerçek `route()`u
    çağırmak, bu kapıyı katalogdaki her değişikliğe bağımlı kılardı."""
    from app import cube_router

    def _ver(cube):
        monkeypatch.setattr(cube_router, "route", lambda q, s, **k: {
            "cube_query": {"cube": cube, "measures": ["x"]}})
    return _ver


def test_YANLIS_KONUDAN_CEVAP_GORULUYOR(_cevapli):
    """🔴🔴 Aletin **körlüğü kapatıldı**: cevaplanmış olmak, doğru cevaplanmış olmak değil.

    Ölçüldü (`Y6`): *«tamir süresi»* artık cevapsız DEĞİL — `kalite` veriyor, oysa tamir
    `bakim`'ın işi. Bu dal olmasaydı alet bir cevap gördüğü an susardı.
    """
    _cevapli("kalite")
    r = menu.incele("tamir süresi ne kadar", SEMA, ("bakim",))
    assert r is not None, "yanlış konudan gelen cevap görünmez kaldı"
    assert r["kova"] == menu.YANLIS_KONU
    assert r["cube"] == "kalite" and "bakim" in r["aday"][0]


def test_BEKLENEN_COKLU_OLABILIR_YANLIS_POZITIF_URETMESIN(_cevapli):
    """⚠ `§101.1` — kendi yanlış-pozitifini üreten bir yüklem, kusurdan pahalıdır.

    `AA13`'ün beklentisi tekti (`parti`) ve `oee` de doğru cevap veriyordu; tek beklenti
    dayatmak aletin **kendi** hatasını üretirdi.
    """
    _cevapli("kalite")
    assert menu.incele("tamir süresi ne kadar", SEMA, ("bakim", "kalite")) is None


def test_HICBIR_SEY_TUTMAZSA_MUTFAK_EKSIGI():
    r = menu.incele("şikayetleri bölgelere göre ver", SEMA, ("sikayet",))
    assert r is not None and r["kova"] == menu.KONU_YOK


def test_KANIT_SORULARI_RAPORUN_DORT_KANITI():
    """⚠ Kabul ölçütünün kendisi: dört kanıt **yazılı** ve beklentileri belli."""
    assert len(menu.KANIT_SORULARI) == 4
    assert all(isinstance(v, tuple) and v for v in menu.KANIT_SORULARI.values())


def test_ALET_KARAR_VERMEZ_RAPOR_URETIR():
    """🔴 `r1_envanteri`'nin dersi: kararı araç verirse bir tenant'ın alan bilgisi
    hepsine dayatılır (ölçüldü: korpus %93,2 → %92,6). Alet **yazmaz**."""
    kaynak = (menu.__file__ and open(menu.__file__, encoding="utf-8").read()) or ""
    for yasak in ("write_text", "yaml.dump", "open(", "cube_synonyms"):
        if yasak == "open(":
            continue   # `--sorular` okuması meşru; YAZMA aranıyor
        assert yasak not in kaynak.split('"""')[-1], f"alet {yasak} ile karar yazıyor"
