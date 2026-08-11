"""🔴 `§B1` — ŞEMA DARALTMA. Garsona giden katalog metni soruya göre budanır.

Ölçüldü (2026-08-11, canlı `demo-boyahane`): **23 küp · 23.729 karakter**, her soruda
(raporun `§4.2`'si birebir). Şema bağlama hatası kurumsal ölçekte SQL hatalarının
**%27,6-33,0'ı**.

Bu kapı ÜÇ şeyi kilitler:
① 🔴 **İndeks ASLA budanmaz** — o `parse_cube_query`'nin beyaz listesi, bir anlatım
   tercihi değil (`build_catalog`'un kendi sözleşmesi).
② **Fail-open bir SAYIYA değil KANITA bağlı** — planın *«aday<2»* kuralı ölçüldü ve
   yetmedi (*«kalite durumunu özetle»* → aday 7, doğru küp aralarında **yok**).
③ 🔴 **`KURAL B`** — `soru` verilmezse metin **bayt bayt** eski.
"""

from app.cube_router import daraltma_adaylari
from app.katalog_metni import build_catalog

_SCHEMA = {
    "models": [],
    "cubes": [
        {"name": "parti", "synonyms": ["ciro", "fire", "parti"],
         "measures": ["toplam_ciro"], "dimensions": ["musteri"],
         "measure_synonyms": {"toplam_ciro": ["ciro"]},
         "dimension_synonyms": {"musteri": ["musteri"]}},
        {"name": "oee", "synonyms": ["oee", "verim", "durus"],
         "measures": ["ort_oee"], "dimensions": ["makine"],
         "measure_synonyms": {"ort_oee": ["oee"]},
         "dimension_synonyms": {"makine": ["makine"]}},
        {"name": "kalite", "synonyms": ["rework", "tamir"],
         "measures": ["toplam_rework_kg"], "dimensions": ["bolum"],
         "measure_synonyms": {"toplam_rework_kg": ["rework"]},
         "dimension_synonyms": {"bolum": ["bolum"]}},
    ],
}


# ── ① İNDEKS DOKUNULMAZ ──────────────────────────────────────────────────────

def test_indeks_asla_budanmaz_yalniz_metin_budanir():
    """🔴 İndeks `parse_cube_query`'nin beyaz listesidir.

    Budansaydı, garsonun döndürdüğü fiş **anlatım tercihiyle daraltılmış** bir sınıra
    karşı doğrulanırdı — `build_catalog`'un kendi cümlesinin ihlali: *«bir kapının
    genişliği, kapıdan geçenin nasıl anlatıldığına bağlı olamaz.»*
    """
    metin, index = build_catalog(_SCHEMA, metin_kupleri={"oee"})
    assert set(index) == {"parti", "oee", "kalite"}, "indeks TAM kalmalı"
    assert "oee" in metin and "kalite" not in metin and "parti" not in metin


def test_budamasiz_cagri_bugunku_metni_uretir():
    """`KURAL B` — `metin_kupleri=None` → bugünkü çıktı, bayt bayt."""
    a, ia = build_catalog(_SCHEMA)
    b, ib = build_catalog(_SCHEMA, metin_kupleri=None)
    assert a == b and ia.keys() == ib.keys()
    for ad in ("parti", "oee", "kalite"):
        assert ad in a


# ── ② FAIL-OPEN KANITA BAĞLI ─────────────────────────────────────────────────

def test_acıklanamayan_icerik_sozcugu_varsa_budama_yok():
    """*«kalite durumunu özetle»* dersi: aday sayısı çok olabilir ama doğru küp
    aralarında olmayabilir. Sayı bir kanıt değildir — kanıt, sorunun her **içerik**
    sözcüğünün katalogla açıklanabilmesidir."""
    assert daraltma_adaylari("ciro zeplin katsayisi", _SCHEMA) is None


def test_islev_sozcugu_budamayi_engellemez():
    """`hangi`/`ne` kapalı bir dilbilgisi sınıfıdır (ADR-0008), konu değildir."""
    karar = daraltma_adaylari("hangi makine oee", _SCHEMA)
    assert karar is not None
    assert "oee" in karar[0]


def test_sinyalsiz_soru_fail_open():
    assert daraltma_adaylari("", _SCHEMA) is None
    assert daraltma_adaylari("bu yıl", _SCHEMA) is None
    assert daraltma_adaylari("ciro", {"cubes": []}) is None


def test_tum_kupler_aday_ise_budama_yapilmaz():
    """Budama yoksa metni ikinci kez kurmanın anlamı yok — `None` döner."""
    tek = {"models": [], "cubes": [_SCHEMA["cubes"][0]]}
    assert daraltma_adaylari("ciro", tek) is None


def test_capraz_kup_sorusunda_IKISI_DE_korunur():
    """🔴 Kartın 3. curl senaryosu: *«ciro ve duruş»* → iki küp de kalmalı.

    Canlıda ölçüldü: garsonun seçtiği küp `makine_duruslari`; aday kümesi onu
    içeriyordu (8/8 kapsama ölçümünün en kritik satırı).
    """
    karar = daraltma_adaylari("ciro ve durus", _SCHEMA)
    assert karar is not None
    adaylar, gerekce = karar
    assert {"parti", "oee"} <= adaylar
    assert "küp" in gerekce and "içerik" in gerekce
