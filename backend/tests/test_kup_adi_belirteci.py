"""🔴 KÜPÜN KENDİ ADI BİR EŞLEŞME BELİRTECİDİR — `§B1` araştırmasının kök bulgusu.

`ilgili_cubelar` yalnız elle yazılmış `synonyms` listesine bakıyordu ve o listeye küpün
adı **bazen** kopyalanmış, bazen unutulmuştu. Ölçüldü (2026-08-11, dört şirket):
**39 küp beyanının 12'sinde (%31)** ad eksik; `ticaret` **dördünde birden**.

Somut kusur: *«kalite durumunu özetle»* → `ilgili_cubelar` altı küp döndürüyordu ve
**`kalite` onların arasında değildi** — oysa canlı cevap `kalite` küpünden geliyor.
"""

from app.cube_router import _kup_adi_belirtecleri, ilgili_cubelar, veri_niyeti_var

# `kalite`nin gerçek beyanı: adı sinonimlerde YOK (canlı katalogdan alındı).
_SCHEMA = {
    "cubes": [
        {"name": "kalite",
         "synonyms": ["rework", "tamir", "yeniden islem", "hata", "kalite hatasi"],
         "measures": ["toplam_rework_kg"], "dimensions": ["bolum"],
         "dimension_synonyms": {"bolum": ["bölüm"]}},
        {"name": "makine_duruslari",
         "synonyms": ["durus nedeni", "durus sebebi"],
         "measures": ["durus_dk"], "dimensions": ["neden"],
         "dimension_synonyms": {"neden": ["neden kodu"]}},
        {"name": "parti",
         "synonyms": ["ciro", "fire", "parti"],          # adı ZATEN var — regresyon ucu
         "measures": ["toplam_ciro"], "dimensions": ["musteri"],
         "dimension_synonyms": {"musteri": ["müşteri"]}},
    ]
}


def _adlar(q):
    return {c["name"] for c in ilgili_cubelar(q, _SCHEMA)}


def test_adi_sinonimde_olmayan_kup_artik_bulunur():
    """Ölçülen kusurun ta kendisi — `kalite` sözcüğü `kalite` küpünü seçmiyordu."""
    assert "kalite" in _adlar("kalite durumunu özetle")


def test_alt_cizgili_ad_bosluklu_yazımla_bulunur():
    """`makine_duruslari` → kullanıcı «makine duruslari» yazar, alt çizgi yazmaz."""
    assert "makine_duruslari" in _adlar("makine duruslari raporu")


def test_adi_zaten_sinonimde_olan_kup_icin_davranis_degismez():
    """`parti` her iki yoldan da bulunur — türev bir EK'tir, bir DEĞİŞİKLİK değil."""
    assert "parti" in _adlar("parti bazında ciro")
    assert "parti" in _adlar("bu yıl ciro")


def test_konusuz_soru_hala_bos_doner():
    """🔴 `§101.1` — yanlış pozitif, kusurun kendisinden pahalıdır.

    Dolgu/sosyal süzgeci çağıranda ve **yukarıda**dır: konu taşımayan bir ifade, küp
    adları belirteç olsa bile hiçbir küp seçmez.
    """
    assert _adlar("teşekkürler") == set()
    assert _adlar("bu yıl") == set()


def test_belirtec_katalogdan_turetilir_liste_yazilmaz():
    """ADR-0008 — yeni sözlük yok; belirteç `name:` alanından **türetilir**."""
    assert _kup_adi_belirtecleri({"name": "kalite"}) == ["kalite"]
    assert _kup_adi_belirtecleri({"name": "makine_duruslari"}) == [
        "makine_duruslari", "makine duruslari"]
    assert _kup_adi_belirtecleri({}) == []
    assert _kup_adi_belirtecleri({"name": "  "}) == []


def test_veri_niyeti_kapisi_da_kazanir():
    """⊙ `ilgili_cubelar` `veri_niyeti_var`'ı besler — çıplak bir küp adı artık
    *«veri sorusu»* sayılır; eskiden sosyal kanada düşebilirdi."""
    assert veri_niyeti_var("kalite", _SCHEMA) is True
    assert veri_niyeti_var("teşekkürler", _SCHEMA) is False
