"""FAZ 5.2 kapısı — **7. tür: *"paylaş / müdüre 3 cümle"***. [bayrak: `tur_paylas`]

## Ölçülen erişilemezlik

*"Müdüre 3 cümle yaz"* niyet olarak **`TUR_ANLAT`'a çok yakın** ama sözlükte *"yaz"* /
*"3 cümle"* olmadığı için yakalanmıyordu → **çalışan, testli bir yetenek bir kelime
yüzünden kullanıcıya kapalı**. `share|public` uç sayısı da **sıfırdı**.

## Dört değişmez — dördü de ayrı ayrı kilitli

**imzalı** · **süreli** · **maskeli** · **tenant-eşleşmeli**. Biri düşerse madde yanlış
yapılmış demektir.
"""

from __future__ import annotations

import time

import pytest

from app import followup, paylasim

#: 🔴 **≥10 GERÇEK İFADE VARYANTI** (5.3 disiplini).
_VARYANTLAR = [
    "mudure 3 cumle yaz",
    "mudure yaz",
    "yoneticiye yaz",
    "patrona yaz",
    "bunu paylas",
    "paylasabilir link ver",
    "link olustur",
    "maille",
    "mail at",
    "uc cumle ile ozetle",
    "iki cumle yaz",
    "sunuma koy",
]


@pytest.mark.parametrize("ifade", _VARYANTLAR)
def test_ON_IKI_GERCEK_IFADE_taninir(ifade):
    """🔴 *Çalışan bir yetenek, bir kelime yüzünden kapalıydı.*"""
    n = followup.sinifla(ifade, baglam_var=True)
    assert n.sinif == followup.SINIF_KONUSMA, (
        f"`{ifade}` konuşma sınıfına girmedi → {n.sinif}/{n.kural}")
    assert n.tur == followup.TUR_PAYLAS


def test_ZAMIR_sarti_ARANMAZ():
    """*"Müdüre 3 cümle yaz"* eldeki cevaba dair olduğunu **hedefiyle** söyler.

    Zamir şartı konsaydı en doğal ifade **yine kapalı kalırdı** — yani düzeltilen kusurun
    aynısı, bir kat aşağıda tekrarlanırdı.
    """
    n = followup.sinifla("mudure 3 cumle yaz", baglam_var=True)
    assert n.tur == followup.TUR_PAYLAS


def test_baglam_YOKKEN_acilmaz():
    assert followup.sinifla("mudure yaz", baglam_var=False).sinif == followup.SINIF_YENI


# --- DÖRT DEĞİŞMEZ ----------------------------------------------------------------

@pytest.fixture(autouse=True)
def _gizli(monkeypatch):
    """İmza anahtarı — testte sabit. ⚠ Gerçek secret **asla** teste yazılmaz."""
    monkeypatch.setattr(paylasim, "_gizli", lambda: b"test-gizli-anahtar")


def test_1_IMZALI_kurcalanmis_token_REDDEDILIR():
    t = paylasim.uret({"question": "x", "tenant": "a"})
    govde, imza = t.split(".", 1)
    with pytest.raises(paylasim.PaylasimHatasi):
        paylasim.coz(f"{govde}.{'A' * len(imza)}")
    # Gövdeyi değiştirmek de yakalanmalı.
    import base64
    import json
    ham = json.loads(base64.urlsafe_b64decode(govde + "=" * (-len(govde) % 4)))
    ham["tenant"] = "baska"
    sahte = base64.urlsafe_b64encode(
        json.dumps(ham, ensure_ascii=False, separators=(",", ":"),
                   sort_keys=True).encode()).decode().rstrip("=")
    with pytest.raises(paylasim.PaylasimHatasi):
        paylasim.coz(f"{sahte}.{imza}")


def test_1b_imza_SABIT_ZAMANLI_karsilastirilir():
    """Normal `==`, token'ı bayt bayt tahmin etmeye açık bir **zamanlama kanalı** bırakır."""
    import ast
    from pathlib import Path

    kaynak = (Path(__file__).resolve().parents[1] / "app/paylasim.py").read_text(
        encoding="utf-8")
    agac = ast.parse(kaynak)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "coz")
    cagrilar = {getattr(c.func, "attr", getattr(c.func, "id", ""))
                for c in ast.walk(fn) if isinstance(c, ast.Call)}
    assert "compare_digest" in cagrilar, (
        "🔴 İmza `hmac.compare_digest` ile karşılaştırılmıyor — zamanlama kanalı açık.")


def test_2_SURELI_ve_SONSUZ_secenegi_YOK():
    t = paylasim.uret({"question": "x"}, ttl=10, simdi=1000.0)
    assert paylasim.coz(t, simdi=1005.0)["question"] == "x"
    with pytest.raises(paylasim.PaylasimHatasi, match="süresi"):
        paylasim.coz(t, simdi=1011.0)
    # Azami ömür KIRPILIR — sınırsız bir link, geri alınamayan bir veri kapısıdır.
    uzun = paylasim.coz(paylasim.uret({"q": 1}, ttl=10**9, simdi=0.0), simdi=0.0)
    assert uzun["exp"] <= paylasim.AZAMI_TTL


def test_3_MASKELI_ve_ikinci_maskeleyici_YOK():
    """🔴 `pii.py` tek çıkış noktasıdır — ikinci bir maskeleyici **ayrışır**."""
    sinif = type("R", (), {})
    r = sinif()
    r.model_dump = lambda: {                              # noqa: ARG005
        "question": "ali@ornek.com icin ciro",
        "note": None, "narration": None, "source": "cube", "view_hint": None,
        "result": {"columns": ["mail"], "rows": [{"mail": "veli@ornek.com"}]},
        "sql": "SELECT * FROM gizli", "cube_query": {"cube": "x"},
    }
    y = paylasim.paylasim_yuku(r)
    assert "ali@ornek.com" not in y["question"], "🔴 soru metni MASKELENMEDİ"
    assert "veli@ornek.com" not in str(y["rows"]), "🔴 satırlar MASKELENMEDİ"
    # 🔴 Çalıştırılabilir sorgu TAŞINMAZ — link bir oturum değildir.
    assert "sql" not in y, "🔴 `sql` paylaşılan yüke sızdı (şema bilgisi sızdırır)"
    assert "cube_query" not in y, (
        "🔴 `cube_query` paylaşılan yüke sızdı — link, veri yüzeyine bir kapı olurdu.")

    # İkinci maskeleyici yok: modül `pii`'yi ÇAĞIRIYOR mu?
    import ast
    from pathlib import Path

    agac = ast.parse((Path(__file__).resolve().parents[1] / "app/paylasim.py")
                     .read_text(encoding="utf-8"))
    adlar = {getattr(n, "attr", "") for n in ast.walk(agac) if isinstance(n, ast.Attribute)}
    assert {"mask_rows", "mask_text"} & adlar, (
        "🔴 `paylasim.py` `pii.py`'yi çağırmıyor — ikinci bir maskeleyici yazılmış olabilir "
        "ve iki maske AYRIŞIR; ayrışan taraf her zaman daha GEVŞEK olanıdır.")


def test_4_TENANT_ESLESMESI_capraz_okumayi_kapatir():
    """🔴 İmza token'ın **gerçekliğini** kanıtlar, okuyanın **hakkını** değil."""
    from fastapi import HTTPException

    from app.routers import paylasim as router

    token = paylasim.uret({"question": "gizli", "tenant": "sirket-a"})

    class _İstek:
        class state:                                       # noqa: N801
            principal = {"tenant_slug": "sirket-b"}

    import app.features as _f

    _eski = _f.resolve_for
    _f.resolve_for = lambda *a, **k: {"tur_paylas"}
    try:
        with pytest.raises(HTTPException) as e:
            router.share_read(token, _İstek())
        assert e.value.status_code == 404, (
            "🔴 403 verilmiş — bir token'ın VAR OLDUĞUNU sızdırmak tahmini kolaylaştırır.")
        # Aynı tenant OKUR:
        _İstek.state.principal = {"tenant_slug": "sirket-a"}
        assert router.share_read(token, _İstek())["question"] == "gizli"
    finally:
        _f.resolve_for = _eski


def test_ANAHTARSIZ_imza_FAIL_CLOSED(monkeypatch):
    """Secret yoksa link **üretilmez** — anahtarsız bir imza, imza değildir."""
    monkeypatch.undo()

    class _S:
        jwt_secret = ""

    monkeypatch.setattr("control_plane.config.get_auth_settings", lambda: _S())
    with pytest.raises(paylasim.PaylasimHatasi, match="jwt_secret"):
        paylasim.uret({"q": 1})


def test_BAYRAK_kayitli_ve_KAPALI():
    from pathlib import Path

    import yaml

    from app.features import FLAG_REGISTRY

    assert "tur_paylas" in FLAG_REGISTRY
    d = yaml.safe_load((Path(__file__).resolve().parents[1] / "demo/packs/features.yml")
                       .read_text(encoding="utf-8"))
    assert d["features"]["tur_paylas"] == "off"
