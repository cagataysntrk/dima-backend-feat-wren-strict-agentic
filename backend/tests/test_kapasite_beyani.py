"""🔴 `G8` — **MENÜ**: yapamadığında NE YAPABİLDİĞİNİ söyler.

`yetenek.py` (KÖK-6) *"yapamam"* diyor ve gerekçesini yazıyordu — ama *"Yapabildiğim: …"*
cümlesi **serbest metin** ve **elle yazılmış örneklerle** doluydu (*"son 6 ayda ciro nasıl
gitti"*). O örnekler hiçbir tenant'ta doğrulanmıyordu: cube yoksa öneri kullanıcıyı
**ikinci bir duvara** çarptırırdı.

🔴 `G8` onları **katalogdan türetir** ve **`route()` ile doğrular**. *Aynı duvara ikinci
kez çarptıran bir chip, chip olmamasından kötüdür.*
"""

from __future__ import annotations

from app.yetenek import Sinir, kapsam_disi, onerileri_kur, yanit_alanlari

_SEMA = {"cubes": [{
    "name": "satis", "synonyms": ["satış", "ciro"],
    "measures": [{"name": "toplam_ciro"}],
    "measure_synonyms_display": {"toplam_ciro": "ciro"},
    "dimensions": [{"name": "sube"}],
    "dimension_labels": {"sube": "şube"},
}]}


def test_ONERILER_route_ile_DOGRULANIR():
    """🔴 Çalışmayan bir öneri BASILMAZ — `ask.py:428`'in disiplini."""
    from app import cube_router

    oneriler = onerileri_kur(_SEMA, tur="forecast")
    for o in oneriler:
        assert cube_router.route(cube_router._norm(o["query"]), _SEMA) is not None, (
            f"doğrulanmamış öneri basıldı: {o['query']!r}")


def test_KATALOGDAN_turetilir_ELLE_YAZILMAZ():
    """Öneriler o tenant'ın **kendi** kataloğundan gelir; sabit örnek yok."""
    oneriler = onerileri_kur(_SEMA, tur="forecast")
    if oneriler:                       # katalog cevap açıyorsa
        assert any("ciro" in o["query"] for o in oneriler)


def test_BOS_KATALOGDA_oneri_YOK():
    """Fail-closed: katalog yoksa uydurma öneri üretilmez."""
    assert onerileri_kur({"cubes": []}, tur="forecast") == []
    assert onerileri_kur(None, tur="forecast") == []


def test_UCUNCU_ONERI_KANALI_ACILMADI():
    """🔴 `AskResponse` zaten `suggestions` ve `next_steps` taşıyor. Üçüncüsü kullanıcıya
    *"hangisi gerçek öneri"* sorusunu sordururdu — mevcut `suggestions` kullanılır."""
    s = Sinir(tur="forecast", kutu="x", mesaj="m", gerekce="g",
              oneriler=[{"label": "ciro", "query": "bu yıl ciro"}])
    alanlar = yanit_alanlari(s, "soru")
    assert "suggestions" in alanlar
    assert "kapasite" not in alanlar, "yeni bir alan açılmış — üçüncü kanal"
    assert alanlar["source"] is None    # hâlâ bir RET


def test_ONERI_YOKSA_alan_da_YOK():
    """Boş bir öneri listesi basmak, *"hiçbir şey yapamıyorum"* demenin gürültülü hâli."""
    s = Sinir(tur="forecast", kutu="x", mesaj="m", gerekce="g")
    assert "suggestions" not in yanit_alanlari(s, "soru")


def test_FORECAST_sinirinda_oneriler_TASINIR():
    """Uçtan uca: kapsam dışı bir soru **hem** reddi **hem** menüyü taşımalı."""
    s = kapsam_disi("bu gidişle yılı nerede kapatırız", _SEMA)
    assert s is not None and s.tur == "forecast"
    assert isinstance(s.oneriler, list)
