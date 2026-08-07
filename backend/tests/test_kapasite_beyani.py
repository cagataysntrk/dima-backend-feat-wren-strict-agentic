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

#: 🔴 **FİKSTÜR BOZUKTU — ve altı testi SESSİZCE ETKİSİZ BIRAKMIŞTI.**
#:
#: Eski hâli `measures`/`dimensions`'ı **sözlük listesi** yazıyordu
#: (`[{"name": "toplam_ciro"}]`). Gerçek şema **düz ad listesi** kullanıyor
#: (`["toplam_ciro"]`) — `cube_router` `cols.get(dname)` diye okur, sözlükte patlar.
#:
#: Sonuç: `onerileri_kur` her öneriyi `route()` ile doğruluyor, `route()` bu fikstürde
#: hiçbir şey bulamıyor, dolayısıyla fonksiyon **`[]`** dönüyordu. Ve dosyadaki testler
#: `for o in oneriler:` / `if oneriler:` üstünde durduğu için **altısı da yeşildi**.
#: `G8`'in tek ürünü hiç sınanmıyordu; bunu bir denetim ajanı buldu.
#:
#: ⚠ Bu, benim `test_r11_ifade_edilemez.py`'de aynı gün düştüğüm hatanın ikizi ve dersi
#: aynı: *bir şemayı hatırlamak, onu okumaktan her zaman daha pahalıdır.*
#: Şekil `wren.schema()`'dan **okundu**, uydurulmadı.
_SEMA = {"cubes": [{
    "name": "satis", "synonyms": ["satış", "ciro"],
    "measures": ["toplam_ciro"],
    "measure_synonyms": {"toplam_ciro": ["ciro", "satis", "hasilat"]},
    "measure_synonyms_display": {"toplam_ciro": "ciro"},
    "dimensions": ["sube"],
    "dimension_labels": {"sube": "şube"},
    "time_dimensions": ["tarih"],
}]}


def test_ONERILER_route_ile_DOGRULANIR():
    """🔴 Çalışmayan bir öneri BASILMAZ — `ask.py:428`'in disiplini."""
    from app import cube_router

    oneriler = onerileri_kur(_SEMA, tur="forecast")
    for o in oneriler:
        assert cube_router.route(cube_router._norm(o["query"]), _SEMA) is not None, (
            f"doğrulanmamış öneri basıldı: {o['query']!r}")


def test_ONERI_URETILIYOR_MU_hic():
    """🔴 **G8'İN TEK ÜRÜNÜ SESSİZCE KAYBOLABİLİRDİ** — denetim bulgusu.

    Bu dosyanın öteki testleri `for o in oneriler:` ve `if oneriler:` üstünde duruyordu:
    `onerileri_kur` **boş dönmeye başlarsa altısı da yeşil kalır** ve *"ama şunu
    yapabilirim"* ekrandan sessizce silinir. `G8`'in varlık sebebi tam olarak o cümleydi.

    *Bir listeyi dolaşan test, listenin boş olmadığını sınamaz — yalnız boş olmadığında
    doğru olduğunu sınar.*
    """
    oneriler = onerileri_kur(_SEMA, tur="forecast")
    assert oneriler, (
        "🔴 `onerileri_kur` HİÇ öneri üretmiyor — `G8`'in tek ürünü yok. Bu dosyanın "
        "geri kalanı boş listede de yeşil kalır; kapı ancak bu satırla gerçektir.")


def test_KATALOGDAN_turetilir_ELLE_YAZILMAZ():
    """Öneriler o tenant'ın **kendi** kataloğundan gelir; sabit örnek yok.

    ⚠ `if oneriler:` KALDIRILDI: boşluk artık `test_ONERI_URETILIYOR_MU_hic`'in
    konusudur ve orada **kırmızı** verir; burada koşulsuz iddia edilir."""
    oneriler = onerileri_kur(_SEMA, tur="forecast")
    assert any("ciro" in o["query"] for o in oneriler), (
        f"öneriler katalogdan türemiyor: {[o['query'] for o in oneriler][:3]}")


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


def test_G6_8_IKI_CUBE_BEYANI_BAYATLAMADI(schema):
    """🔴 `G6.8` (`Ö12`'nin chip yarısı) — **bir sınır beyanı bayatlamıştı.**

    Eski metin *"onları tek bir tabloda birleştirmiyorum"* diyordu. `G6.5`'ten sonra bu
    **artık doğru değil**: `blend` mutfakta çalışıyor, `blend_uyumlu` grain'i doğruluyor,
    Intent-JSON onu ifade edebiliyor.

    ⚠ *Bir sınır beyanı, sınır değiştiğinde kendiliğinden güncellenmez — ve güncellenmeyen
    bir beyan, kullanıcıya sahip olduğumuz yeteneği YOK diye söyler.*
    *Yanlış bir «yapamam», yanlış bir «yapabilirim» kadar pahalıdır.*

    Ayrım kilitleniyor: **yan yana** ✅ (`blend`) · **ilişki** ⊘ (v2 · II-D).
    """
    from app import yetenek

    ikili = yetenek._iki_cube_olcusu("fire ve maas ortalamasi", schema)
    if not ikili:
        import pytest
        pytest.skip("⊘ bu katalogda iki-cube vakası kurulmadı — vaka bayat")
    s = yetenek.kapsam_disi("fire ve maas ortalamasi", schema)
    assert s is not None and s.tur == "iki_cube"
    assert "birleştirmiyorum" not in s.mesaj, (
        "🔴 BAYAT BEYAN: `blend` indi, metin hâlâ 'birleştirmiyorum' diyor")
    assert "ilişki" in s.mesaj.lower(), "🔴 yapamadığımız şey (ilişki) adlandırılmamış"
    assert "yan yana" in s.mesaj.lower(), "🔴 yapabildiğimiz şey söylenmemiş"
    assert "Ö12" in s.gerekce
