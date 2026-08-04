"""FAZ 0.18 — **METRİK KAYDI = HAKEM.** Belgenin tek en büyük ölçülmüş kazancı.

## Ölçülen kök neden

`CLARIFY:konu` **%11,5** + yanlış-cube **%6,8** ≈ **turların ~%18'i** — ve ikisinin de
**kanıtlanmış baskın kökü aynı**: bir iş terimi **iki cube tarafından sahiplenilmiş,
hakem yok**. Korpus birebir gösteriyor: boyahane yanlış-cube listesinin **ilk 10'unun
10'u** `elektrik`; atiksan'ın (**%98, en iyi şirket**) **ilk 9'unun 9'u** `satış`.

Canlı bir kullanıcı turu aynı sınıfı **bağımsız olarak** buldu: *"bu yıl bakiye"* →
`cari` (**₺11,86 milyon**), *"mizanda bu yıl bakiye"* → `mizan` (**₺0**). Sistem birini
**kura ile** seçti, sormadı, seçtiğini de yazmadı.

## Maddenin kendi kendine güvenli olması

Taslak `sahiplenilen_terimler: []` ile gelir → `hakem()` `None` döner → `_match_cube`
bugünkü zinciri **aynen** koşar. Yani madde **çakışmayı görünür kılar**, kararı vermez;
karar **FAZ 3.1'in sahiplik turudur**. Görünmeyen bir çakışma düzeltilemez.
"""

from __future__ import annotations

import inspect

import pytest

from app import metrik_kaydi as mk

#: Üç cube'un aynı terimi paylaştığı sentetik katalog — `elektrik` vakasının şekli.
SEMA = {
    "cubes": [
        {"name": "enerji_makine",
         "measure_synonyms": {"tuketim": ["elektrik", "elektrik tüketimi"]}},
        {"name": "enerji_tesis",
         "measure_synonyms": {"tuketim": ["elektrik", "tesis elektriği"]}},
        {"name": "surdurulebilirlik",
         "measure_synonyms": {"karbon": ["elektrik", "karbon"]}},
        {"name": "parti",
         "measure_synonyms": {"fire_kg": ["fire", "fire kilogram"]}},
    ]
}


def test_CAKISMA_ENVANTERI_olculuyor():
    """Çakışma bir **olgudur**, bayrağa bağlı değildir: hangi terimi kaç cube
    sahipleniyor — bu her zaman sorulabilmeli."""
    c = mk.cakisan_terimler(SEMA)
    assert "elektrik" in c, f"üç cube'un paylaştığı terim görülmedi: {c}"
    assert c["elektrik"] == ["enerji_makine", "enerji_tesis", "surdurulebilirlik"]
    assert "fire" not in c, "tek sahibi olan terim çakışma sayıldı"


def test_TASLAK_KARAR_VERMEZ_sadece_gorunur_kilar():
    """🔴 **Maddenin kendi kendine güvenli olmasının mekanizması.** Taslak *"bu terim
    çakışıyor"* der, *"sahibi şudur"* **demez** — `sahiplenilen_terimler` BOŞ başlar."""
    kayit = mk.taslak_uret(SEMA)
    assert kayit, "taslak boş üretildi"
    for k in kayit:
        assert k["sahiplenilen_terimler"] == [], \
            f"taslak bir SAHİPLİK KARARI vermiş: {k}"
        assert k["olusturulma_yontemi"] == "otomatik_taslak"
        assert len(k["adaylar"]) > 1, "çakışmayan terim taslağa girmiş"


def test_HAKEM_bos_kayitta_KARAR_VERMEZ():
    """Boş sahiplik → `None` → `_match_cube` bugünkü yolunu izler. **GERİ AL'ın özü.**"""
    kayit = mk.taslak_uret(SEMA)
    assert mk.hakem("elektrik", kayit) is None
    assert mk.hakem("elektrik", None) is None
    assert mk.hakem("", kayit) is None


def test_HAKEM_TEK_SAHIPTE_karar_verir():
    """Sahiplik doldurulduğunda hakem **kesin** karar verir — `elektrik` → `enerji_makine`."""
    kayit = [{"terim": "elektrik", "adaylar": ["enerji_makine", "enerji_tesis"],
              "sahiplenilen_terimler": ["enerji_makine"]}]
    assert mk.hakem("elektrik", kayit) == "enerji_makine"


def test_CIFT_SAHIPLIK_REDDEDILIR_fail_closed():
    """🔴 İki sahip, hakemsizlikten **daha kötüdür**: hakem yine yoktur ama üstüne bir de
    *"hakem var"* beyanı eklenir — beyan ile kodun ayrıştığı hâl."""
    kotu = [{"terim": "elektrik", "adaylar": ["a", "b"],
             "sahiplenilen_terimler": ["enerji_makine", "enerji_tesis"]}]
    ihlaller = mk.cift_sahiplik_denetle(kotu)
    assert ihlaller and "elektrik" in ihlaller[0]

    sema = dict(SEMA)
    orj = mk.taslak_uret
    mk.taslak_uret = lambda _s: kotu                      # type: ignore[assignment]
    try:
        with pytest.raises(ValueError, match="ÇİFT SAHİPLİK"):
            mk.semaya_yaz(sema, acik=True)
    finally:
        mk.taslak_uret = orj                              # type: ignore[assignment]
    assert mk.SEMA_ANAHTARI not in sema, "çelişen kayıt ŞEMAYA YAZILDI (fail-closed değil)"


def test_BAYRAK_KAPALI_iken_SEMAYA_HIC_YAZILMAZ():
    """**GERİ AL:** anahtar yoksa `cube_router` kaydı hiç görmez → davranış birebir bugünkü."""
    sema = {"cubes": SEMA["cubes"], mk.SEMA_ANAHTARI: [{"terim": "x"}]}
    mk.semaya_yaz(sema, acik=False)
    assert mk.SEMA_ANAHTARI not in sema, "bayrak kapalıyken kayıt şemada KALDI"


def test_MATCH_CUBE_ILK_SATIRI_paralel_yol_DEGIL():
    """🔴 Kayıt `_match_cube`'un **ilk satırıdır**. Paralel bir eşleştirme yolu açmak,
    aynı sorunun iki sahibini yaratmak olurdu — bu deponun 1 numaralı kusuru."""
    from app import cube_router

    govde = inspect.getsource(cube_router._match_cube)
    i_kayit = govde.index('schema.get("metrik_kaydi")')
    i_hits = govde.index('hits = [c for c in schema.get("cubes", [])')
    assert i_kayit < i_hits, (
        "metrik kaydı bugünkü zincirden SONRA sorulyor — bu bir paralel yoldur, "
        "ilk satır değil. Hakem, keyfi kuraldan ÖNCE gelmeli.")
    assert "from app.metrik_kaydi import hakem" in govde, \
        "ikinci bir hakem uygulaması yazılmış olabilir — tek sahip `metrik_kaydi.hakem`"


def test_CUBE_ROUTER_BAYRAK_OKUMUYOR():
    """`cube_router`'ın saflığı **bilinçli**: bayrak, ayarların erişilebilir olduğu
    derleme sınırında durur. Sıcak yola bayrak sızarsa determinizm iddiası çürür."""
    from app import cube_router

    kaynak = inspect.getsource(cube_router)
    assert "resolve_for" not in kaynak, \
        "cube_router bayrak okumaya başlamış — deterministik saflık bozuldu"


def test_HAKEM_KARARI_MATCH_CUBE_uzerinde_ETKILI():
    """Uçtan uca: kayıt bir sahip beyan ederse `_match_cube` **o cube'u** döndürür."""
    from app import cube_router

    sema = {
        "cubes": [
            {"name": "enerji_makine", "synonyms": ["enerji"],
             "measures": ["tuketim"], "dimensions": [],
             "measure_synonyms": {"tuketim": ["elektrik"]}},
            {"name": "enerji_tesis", "synonyms": ["tesis"],
             "measures": ["tuketim"], "dimensions": [],
             "measure_synonyms": {"tuketim": ["elektrik"]}},
        ],
        "metrik_kaydi": [{"terim": "elektrik", "adaylar": ["enerji_makine", "enerji_tesis"],
                          "sahiplenilen_terimler": ["enerji_tesis"]}],
    }
    sonuc = cube_router._match_cube("bu yıl elektrik", sema)
    assert sonuc is not None and sonuc["name"] == "enerji_tesis", (
        f"hakem kararı uygulanmadı: {sonuc}")

    # Kayıt kaldırılınca bugünkü (keyfi) zincir geri gelir — GERİ AL kanıtı.
    sema.pop("metrik_kaydi")
    cube_router._match_cube("bu yıl elektrik", sema)      # çökmemeli
